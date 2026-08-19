"""Tests for validated generation, retries, fallback, and sync behaviour."""

from __future__ import annotations

import json
from typing import Any, Dict, List

import pytest

from pipeline.nlp.exceptions import LLMGenerationError
from pipeline.nlp.llm_client import LLMClient
from pipeline.nlp.providers import FakeProvider, LLMProvider


class SequenceProvider(LLMProvider):
    """Return responses in order so retry behaviour can be tested."""

    name = "sequence"
    model = "sequence-model"

    def __init__(self, responses: List[str | Exception]) -> None:
        self.responses = list(responses)
        self.calls = 0
        self.user_prompts: List[str] = []

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int,
        temperature: float,
    ) -> str:
        self.calls += 1
        self.user_prompts.append(user_prompt)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.mark.asyncio
async def test_client_returns_validated_feedback(
    valid_feedback_dict: Dict[str, Any],
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    provider = FakeProvider(valid_feedback_dict)
    client = LLMClient(provider=provider, fallback_on_error=False)

    result = await client.generate_feedback(parser_array_bounds_output)

    assert result.provider == "fake"
    assert result.model == "fake-model"
    assert result.used_fallback is False
    assert result.feedback.title == valid_feedback_dict["title"]
    assert result.latency_ms >= 0
    assert len(provider.calls) == 1
    assert "array_bounds" in provider.calls[0]["user_prompt"]
    assert provider.calls[0]["max_tokens"] == 1400
    assert provider.calls[0]["temperature"] == 0.2


@pytest.mark.asyncio
async def test_invalid_response_is_retried_then_succeeds(
    valid_feedback_dict: Dict[str, Any],
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    provider = SequenceProvider(
        [
            json.dumps({"title": "incomplete"}),
            json.dumps(valid_feedback_dict),
        ]
    )
    client = LLMClient(
        provider=provider,
        validation_attempts=2,
        fallback_on_error=False,
    )

    result = await client.generate_feedback(parser_array_bounds_output)

    assert result.used_fallback is False
    assert provider.calls == 2
    assert "previous response failed application validation" in provider.user_prompts[1]


@pytest.mark.asyncio
async def test_malformed_json_uses_fallback_when_enabled(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    provider = FakeProvider("not-json")
    client = LLMClient(
        provider=provider,
        validation_attempts=2,
        fallback_on_error=True,
    )

    result = await client.generate_feedback(parser_array_bounds_output)

    assert result.used_fallback is True
    assert result.feedback.confidence == "low"
    assert "array" in result.feedback.title.lower()
    assert len(provider.calls) == 2


@pytest.mark.asyncio
async def test_malformed_json_raises_when_fallback_disabled(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    provider = FakeProvider("not-json")
    client = LLMClient(
        provider=provider,
        validation_attempts=2,
        fallback_on_error=False,
    )

    with pytest.raises(LLMGenerationError, match="valid pedagogical feedback"):
        await client.generate_feedback(parser_array_bounds_output)

    assert len(provider.calls) == 2


@pytest.mark.asyncio
async def test_provider_error_uses_fallback(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    provider = FakeProvider(
        response={},
        error=LLMGenerationError("temporary provider failure"),
    )
    client = LLMClient(provider=provider, fallback_on_error=True)

    result = await client.generate_feedback(parser_array_bounds_output)

    assert result.used_fallback is True
    assert result.feedback.root_cause == "array upper bound violated"


@pytest.mark.asyncio
async def test_provider_error_is_raised_when_fallback_disabled(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    provider = FakeProvider(
        response={},
        error=LLMGenerationError("temporary provider failure"),
    )
    client = LLMClient(
        provider=provider,
        validation_attempts=1,
        fallback_on_error=False,
    )

    with pytest.raises(LLMGenerationError, match="valid pedagogical feedback"):
        await client.generate_feedback(parser_array_bounds_output)


@pytest.mark.asyncio
async def test_fallback_includes_location_and_last_trace_state(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    client = LLMClient(
        provider=FakeProvider("invalid-json"),
        validation_attempts=1,
        fallback_on_error=True,
    )

    result = await client.generate_feedback(parser_array_bounds_output)

    assert result.used_fallback is True
    assert any("submission.cpp" in item and "line 7" in item for item in result.feedback.evidence)
    assert any("values[i] = 5" in item for item in result.feedback.evidence)


def test_sync_generation_works_outside_event_loop(
    valid_feedback_dict: Dict[str, Any],
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    client = LLMClient(
        provider=FakeProvider(valid_feedback_dict),
        fallback_on_error=False,
    )

    result = client.generate_feedback_sync(parser_array_bounds_output)

    assert result.used_fallback is False
    assert result.feedback.confidence == "high"


@pytest.mark.asyncio
async def test_sync_generation_rejects_active_event_loop(
    valid_feedback_dict: Dict[str, Any],
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    client = LLMClient(provider=FakeProvider(valid_feedback_dict))

    with pytest.raises(RuntimeError, match="active event loop"):
        client.generate_feedback_sync(parser_array_bounds_output)


def test_validation_attempts_must_be_positive(
    valid_feedback_dict: Dict[str, Any],
) -> None:
    with pytest.raises(ValueError, match="at least 1"):
        LLMClient(
            provider=FakeProvider(valid_feedback_dict),
            validation_attempts=0,
        )
