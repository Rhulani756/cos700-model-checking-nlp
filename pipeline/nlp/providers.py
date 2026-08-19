from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Dict

from .exceptions import ConfigurationError, LLMGenerationError


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Return a JSON string generated according to output_schema."""


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 45.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ConfigurationError("ANTHROPIC_API_KEY is required")
        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ConfigurationError(
                "Install the Anthropic SDK with: pip install anthropic"
            ) from exc

        self.model = model
        self._client = Anthropic(
            api_key=api_key,
            timeout=timeout_seconds,
            max_retries=max_retries,
        )

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int,
        temperature: float,
    ) -> str:
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                output_config={
                    "format": {
                        "type": "json_schema",
                        "schema": output_schema,
                    }
                },
            )
        except Exception as exc:
            raise LLMGenerationError("Anthropic request failed: %s" % exc) from exc

        if getattr(response, "stop_reason", None) == "max_tokens":
            raise LLMGenerationError("Anthropic response was truncated at max_tokens")
        if getattr(response, "stop_reason", None) == "refusal":
            raise LLMGenerationError("Anthropic refused to generate feedback")

        text_blocks = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]
        text = "".join(text_blocks).strip()
        if not text:
            raise LLMGenerationError("Anthropic returned no text content")
        return text


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float = 45.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ConfigurationError("GEMINI_API_KEY is required")
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise ConfigurationError(
                "Install the Google Gen AI SDK with: pip install google-genai"
            ) from exc

        self.model = model
        self._client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=int(timeout_seconds * 1000),
                retry_options=types.HttpRetryOptions(
                    attempts=max_retries + 1,
                    initial_delay=1,
                    max_delay=8,
                ),
            ),
        )

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int,
        temperature: float,
    ) -> str:
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config={
                    "system_instruction": system_prompt,
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                    "response_mime_type": "application/json",
                    "response_json_schema": output_schema,
                },
            )
        except Exception as exc:
            raise LLMGenerationError("Gemini request failed: %s" % exc) from exc

        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise LLMGenerationError("Gemini returned no text content")
        return text


class FakeProvider(LLMProvider):
    """Small deterministic provider useful in unit and integration tests."""

    name = "fake"
    model = "fake-model"

    def __init__(self, response: Dict[str, Any] | str, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.calls = []

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int,
        temperature: float,
    ) -> str:
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "output_schema": output_schema,
                "max_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        if self._error is not None:
            raise self._error
        if isinstance(self._response, str):
            return self._response
        return json.dumps(self._response)