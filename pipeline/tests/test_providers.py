"""Unit tests for provider adapters without making network requests."""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, Dict

import pytest

from pipeline.nlp.exceptions import ConfigurationError, LLMGenerationError
from pipeline.nlp.providers import AnthropicProvider, FakeProvider, GeminiProvider


def test_fake_provider_returns_dictionary_as_json(
    valid_feedback_dict: Dict[str, Any],
) -> None:
    provider = FakeProvider(valid_feedback_dict)

    response = provider.generate_json(
        "system",
        "user",
        {"type": "object"},
        500,
        0.2,
    )

    assert json.loads(response) == valid_feedback_dict
    assert len(provider.calls) == 1
    assert provider.calls[0]["system_prompt"] == "system"
    assert provider.calls[0]["user_prompt"] == "user"


def test_fake_provider_returns_string_unchanged() -> None:
    provider = FakeProvider('{"ok": true}')

    response = provider.generate_json("s", "u", {}, 100, 0.0)

    assert response == '{"ok": true}'


def test_fake_provider_raises_configured_error() -> None:
    provider = FakeProvider({}, error=RuntimeError("test failure"))

    with pytest.raises(RuntimeError, match="test failure"):
        provider.generate_json("s", "u", {}, 100, 0.0)


def test_anthropic_requires_api_key() -> None:
    with pytest.raises(ConfigurationError, match="ANTHROPIC_API_KEY"):
        AnthropicProvider(api_key="", model="model")


def test_gemini_requires_api_key() -> None:
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
        GeminiProvider(api_key="", model="model")


def test_anthropic_generate_json_combines_text_blocks() -> None:
    provider = AnthropicProvider.__new__(AnthropicProvider)
    provider.model = "test-model"
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(
                stop_reason="end_turn",
                content=[
                    SimpleNamespace(type="text", text='{"title":'),
                    SimpleNamespace(type="tool_use", text="ignored"),
                    SimpleNamespace(type="text", text='"ok"}'),
                ],
            )
        )
    )

    response = provider.generate_json("system", "user", {}, 100, 0.2)

    assert response == '{"title":"ok"}'


@pytest.mark.parametrize(
    ("stop_reason", "message"),
    [
        ("max_tokens", "truncated"),
        ("refusal", "refused"),
    ],
)
def test_anthropic_stop_reasons_raise(
    stop_reason: str,
    message: str,
) -> None:
    provider = AnthropicProvider.__new__(AnthropicProvider)
    provider.model = "test-model"
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(
                stop_reason=stop_reason,
                content=[],
            )
        )
    )

    with pytest.raises(LLMGenerationError, match=message):
        provider.generate_json("system", "user", {}, 100, 0.2)


def test_anthropic_request_failure_is_wrapped() -> None:
    def fail(**kwargs: Any) -> None:
        raise RuntimeError("network unavailable")

    provider = AnthropicProvider.__new__(AnthropicProvider)
    provider.model = "test-model"
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(create=fail)
    )

    with pytest.raises(LLMGenerationError, match="Anthropic request failed"):
        provider.generate_json("system", "user", {}, 100, 0.2)


def test_anthropic_empty_text_is_rejected() -> None:
    provider = AnthropicProvider.__new__(AnthropicProvider)
    provider.model = "test-model"
    provider._client = SimpleNamespace(
        messages=SimpleNamespace(
            create=lambda **kwargs: SimpleNamespace(
                stop_reason="end_turn",
                content=[],
            )
        )
    )

    with pytest.raises(LLMGenerationError, match="no text content"):
        provider.generate_json("system", "user", {}, 100, 0.2)


def test_gemini_generate_json_returns_response_text() -> None:
    provider = GeminiProvider.__new__(GeminiProvider)
    provider.model = "test-model"
    provider._client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: SimpleNamespace(
                text='{"title": "ok"}'
            )
        )
    )

    response = provider.generate_json("system", "user", {}, 100, 0.2)

    assert response == '{"title": "ok"}'


def test_gemini_request_failure_is_wrapped() -> None:
    def fail(**kwargs: Any) -> None:
        raise RuntimeError("network unavailable")

    provider = GeminiProvider.__new__(GeminiProvider)
    provider.model = "test-model"
    provider._client = SimpleNamespace(
        models=SimpleNamespace(generate_content=fail)
    )

    with pytest.raises(LLMGenerationError, match="Gemini request failed"):
        provider.generate_json("system", "user", {}, 100, 0.2)


def test_gemini_empty_text_is_rejected() -> None:
    provider = GeminiProvider.__new__(GeminiProvider)
    provider.model = "test-model"
    provider._client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=lambda **kwargs: SimpleNamespace(text="   ")
        )
    )

    with pytest.raises(LLMGenerationError, match="no text content"):
        provider.generate_json("system", "user", {}, 100, 0.2)
