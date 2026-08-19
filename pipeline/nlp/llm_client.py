<<<<<<< HEAD
# Constructs prompts from structured counterexample and queries LLM

def generate_feedback(structured_counterexample: dict) -> str:
    pass
=======
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict

from pydantic import ValidationError

from pathlib import Path

from dotenv import load_dotenv
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_FILE)

from .exceptions import ConfigurationError, LLMGenerationError
from .feedback_enrichment import enrich_with_diagram_async
from .prompt_builder import PROMPT_VERSION, PromptBuilder
from .providers import AnthropicProvider, GeminiProvider, LLMProvider
from .schemas import (
    Counterexample,
    FeedbackGenerationResult,
    PedagogicalFeedback,
    ViolationType,
)

logger = logging.getLogger(__name__)


DEFAULT_MODELS = {
    "anthropic": "claude-haiku-4-5-20251001",
    "gemini": "gemini-3.1-flash-lite",
}


class LLMClient:
    """Generate validated pedagogical feedback from normalized parser output."""

    def __init__(
        self,
        provider: LLMProvider,
        prompt_builder: PromptBuilder | None = None,
        max_tokens: int = 1400,
        temperature: float = 0.5,
        validation_attempts: int = 2,
        fallback_on_error: bool = True,
        include_diagram: bool = True,
    ) -> None:
        if validation_attempts < 1:
            raise ValueError("validation_attempts must be at least 1")
        self.provider = provider
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.validation_attempts = validation_attempts
        self.fallback_on_error = fallback_on_error
        self.include_diagram = include_diagram

    @classmethod
    def from_env(cls) -> "LLMClient":
        provider_name = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
        model = os.getenv("LLM_MODEL", DEFAULT_MODELS.get(provider_name, "")).strip()
        if not model:
            raise ConfigurationError("LLM_MODEL must be configured")

        timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "45"))
        max_retries = int(os.getenv("LLM_MAX_RETRIES", "2"))

        if provider_name == "anthropic":
            provider: LLMProvider = AnthropicProvider(
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                model=model,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
            )
        elif provider_name == "gemini":
            provider = GeminiProvider(
                api_key=os.getenv("GEMINI_API_KEY", ""),
                model=model,
                timeout_seconds=timeout_seconds,
                max_retries=max_retries,
            )
        else:
            raise ConfigurationError(
                "LLM_PROVIDER must be either 'anthropic' or 'gemini'"
            )

        return cls(
            provider=provider,
            max_tokens=int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "1400")),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
            validation_attempts=int(os.getenv("LLM_VALIDATION_ATTEMPTS", "2")),
            fallback_on_error=os.getenv("LLM_FALLBACK_ON_ERROR", "true").lower()
            in {"1", "true", "yes"},
            include_diagram=os.getenv("LLM_INCLUDE_DIAGRAM", "true").lower()
            in {"1", "true", "yes"},
        )

    async def generate_feedback(
        self, parser_output: Counterexample | Dict[str, Any]
    ) -> FeedbackGenerationResult:
        counterexample = (
            parser_output
            if isinstance(parser_output, Counterexample)
            else Counterexample.model_validate(parser_output)
        )
        system_prompt, user_prompt = self.prompt_builder.build(counterexample)
        # logger.debug("SYSTEM PROMPT:\n%s", system_prompt)
        # logger.debug("USER PROMPT:\n%s", user_prompt)
        output_schema = PedagogicalFeedback.model_json_schema()

        start = time.perf_counter()
        try:
            feedback = await self._generate_validated(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                output_schema=output_schema,
            )
            used_fallback = False
        except Exception as exc:
            if not self.fallback_on_error:
                if isinstance(exc, LLMGenerationError):
                    raise
                raise LLMGenerationError(str(exc)) from exc
            feedback = self._build_fallback(counterexample)
            used_fallback = True

        latency_ms = int((time.perf_counter() - start) * 1000)
        result = FeedbackGenerationResult(
            feedback=feedback,
            provider=self.provider.name,
            model=self.provider.model,
            prompt_version=PROMPT_VERSION,
            used_fallback=used_fallback,
            latency_ms=latency_ms,
        )

        if self.include_diagram:
            result = await self._safe_enrich_with_diagram(result, counterexample)

        return result

    async def _safe_enrich_with_diagram(
        self,
        result: FeedbackGenerationResult,
        counterexample: Counterexample,
    ) -> FeedbackGenerationResult:
        """Diagram generation must never take down an otherwise-valid response.

        enrich_with_diagram_async already catches DiagramRenderError
        internally. This is a second, broader net around it, so a bug in
        diagram construction itself (not just a render-server failure)
        degrades to a missing diagram instead of losing the text feedback
        that already succeeded.
        """

        try:
            return await enrich_with_diagram_async(result, counterexample)
        except Exception as exc:  # noqa: BLE001 - diagram failures are always non-fatal
            logger.warning("Diagram enrichment failed unexpectedly: %s", exc)
            result.diagram_render_error = str(exc)
            return result

    def generate_feedback_sync(
        self, parser_output: Counterexample | Dict[str, Any]
    ) -> FeedbackGenerationResult:
        """Synchronous helper for CLI scripts and the standalone pipeline.

        Do not call this helper from an already-running event loop. FastAPI
        routes should await generate_feedback() instead.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.generate_feedback(parser_output))
        raise RuntimeError(
            "generate_feedback_sync() cannot run inside an active event loop; "
            "await generate_feedback() instead"
        )

    async def _generate_validated(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
    ) -> PedagogicalFeedback:
        last_error: Exception | None = None
        current_prompt = user_prompt

        for attempt in range(self.validation_attempts):
            try:
                raw_response = await asyncio.to_thread(
                    self.provider.generate_json,
                    system_prompt,
                    current_prompt,
                    output_schema,
                    self.max_tokens,
                    self.temperature,
                )
                return PedagogicalFeedback.model_validate_json(raw_response)
            except (json.JSONDecodeError, ValidationError, LLMGenerationError) as exc:
                last_error = exc
                if attempt + 1 < self.validation_attempts:
                    current_prompt = user_prompt + (
                        "\n\nThe previous response failed application validation. "
                        "Regenerate the complete feedback object and obey every schema field. "
                        "Do not refer to the previous response."
                    )

        raise LLMGenerationError(
            "Provider did not return valid pedagogical feedback: %s" % last_error
        )

    @staticmethod
    def _build_fallback(counterexample: Counterexample) -> PedagogicalFeedback:
        location = LLMClient._format_location(counterexample)
        evidence = [counterexample.message.strip()]
        if location:
            evidence.append("The checker reports the violation at %s." % location)

        trace_evidence = LLMClient._last_trace_evidence(counterexample)
        if trace_evidence:
            evidence.append(trace_evidence)

        property_data = {
            ViolationType.ARRAY_BOUNDS: {
                "title": "Array access may be outside the valid range",
                "concept": (
                    "C++ array indices must stay between 0 and one less than the number "
                    "of elements. Accessing another position can read or overwrite unrelated memory."
                ),
                "changes": [
                    "Check the loop boundary and any index calculation used at the reported line.",
                    "Confirm that the index is at least 0 and strictly smaller than the array size before access.",
                ],
                "question": "What are the smallest and largest valid indices for this array?",
            },
            ViolationType.NULL_SAFETY: {
                "title": "A null pointer may be dereferenced",
                "concept": (
                    "A null pointer does not refer to an object. Using *pointer or pointer->member "
                    "when it is null has undefined behaviour."
                ),
                "changes": [
                    "Trace where the pointer is assigned and identify the path on which it remains null.",
                    "Validate the pointer before dereferencing it, and handle the null case explicitly.",
                ],
                "question": "Which condition guarantees that the pointer refers to a valid object?",
            },
            ViolationType.LOOP_TERMINATION: {
                "title": "The loop may not reach its terminating condition",
                "concept": (
                    "A loop terminates only when its condition eventually becomes false. The checker "
                    "could not establish that this happens within the configured bound."
                ),
                "changes": [
                    "Identify the variables used by the loop condition and confirm that every path updates them.",
                    "Check that each update moves the variables toward making the condition false.",
                ],
                "question": "Which value changes on every iteration and why must it eventually stop the loop?",
            },
            ViolationType.DIVISION_BY_ZERO: {
                "title": "The divisor can become zero",
                "concept": (
                    "Integer or floating-point division requires a valid divisor. A zero divisor can "
                    "cause undefined behaviour, a runtime failure, or an invalid result."
                ),
                "changes": [
                    "Find how the divisor obtains its value on the failing path.",
                    "Reject or handle zero before performing the division, or strengthen the input precondition.",
                ],
                "question": "What program behaviour should occur when the divisor is zero?",
            },
        }[counterexample.violation_type]

        return PedagogicalFeedback(
            title=property_data["title"],
            summary=(
                "The model checker found an execution path that violates the %s property. "
                "The detailed language-model explanation was unavailable, so this is conservative fallback feedback."
                % counterexample.violation_type.value.replace("_", " ")
            ),
            root_cause=counterexample.message.strip(),
            evidence=evidence,
            execution_path=[
                "Review the checker trace leading to the reported location.",
                "Inspect the final state and variable values immediately before the property fails.",
            ],
            why_it_matters=property_data["concept"],
            suggested_changes=property_data["changes"],
            example_fix="",
            check_your_understanding=property_data["question"],
            confidence="low",
        )

    @staticmethod
    def _format_location(counterexample: Counterexample) -> str:
        parts = []
        if counterexample.file:
            parts.append(counterexample.file)
        if counterexample.line is not None:
            parts.append("line %d" % counterexample.line)
        if counterexample.function:
            parts.append("function %s" % counterexample.function)
        return ", ".join(parts)

    @staticmethod
    def _last_trace_evidence(counterexample: Counterexample) -> str:
        if not counterexample.trace:
            return ""
        final_step = counterexample.trace[-1]
        variable_text = ", ".join(
            "%s=%s" % (variable.name, variable.value)
            for variable in final_step.variables[:6]
        )
        details = "The final recorded trace step is '%s'" % final_step.event
        if variable_text:
            details += " with %s" % variable_text
        return details + "."
>>>>>>> origin/feature/ui+pipeline
