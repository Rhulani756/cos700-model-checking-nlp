"""Tests for environment-driven LLMClient configuration."""

from __future__ import annotations

from typing import Any, Dict

import pytest

import pipeline.nlp.llm_client as llm_client_module
from pipeline.nlp.exceptions import ConfigurationError
from pipeline.nlp.llm_client import LLMClient


class CapturingProvider:
    """Provider stub that records constructor arguments from from_env()."""

    name = "captured"

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.model = str(kwargs["model"])

    def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        output_schema: Dict[str, Any],
        max_tokens: int,
        temperature: float,
    ) -> str:
        raise AssertionError("This provider is only used for configuration tests")


def clear_llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_TIMEOUT_SECONDS",
        "LLM_MAX_RETRIES",
        "LLM_MAX_OUTPUT_TOKENS",
        "LLM_TEMPERATURE",
        "LLM_VALIDATION_ATTEMPTS",
        "LLM_FALLBACK_ON_ERROR",
        "GEMINI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_environment_selects_gemini(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(llm_client_module, "GeminiProvider", CapturingProvider)

    client = LLMClient.from_env()

    assert isinstance(client.provider, CapturingProvider)
    assert client.provider.kwargs == {
        "api_key": "test-key",
        "model": "gemini-3.1-flash-lite",
        "timeout_seconds": 45.0,
        "max_retries": 2,
    }
    assert client.max_tokens == 1400
    assert client.temperature == 0.2
    assert client.validation_attempts == 2
    assert client.fallback_on_error is True


def test_anthropic_environment_is_applied(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("LLM_MODEL", "test-claude")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "12.5")
    monkeypatch.setenv("LLM_MAX_RETRIES", "4")
    monkeypatch.setenv("LLM_MAX_OUTPUT_TOKENS", "900")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.1")
    monkeypatch.setenv("LLM_VALIDATION_ATTEMPTS", "3")
    monkeypatch.setenv("LLM_FALLBACK_ON_ERROR", "no")
    monkeypatch.setattr(llm_client_module, "AnthropicProvider", CapturingProvider)

    client = LLMClient.from_env()

    assert isinstance(client.provider, CapturingProvider)
    assert client.provider.kwargs == {
        "api_key": "anthropic-key",
        "model": "test-claude",
        "timeout_seconds": 12.5,
        "max_retries": 4,
    }
    assert client.max_tokens == 900
    assert client.temperature == 0.1
    assert client.validation_attempts == 3
    assert client.fallback_on_error is False


def test_unsupported_provider_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "unsupported")
    monkeypatch.setenv("LLM_MODEL", "some-model")

    with pytest.raises(ConfigurationError, match="either 'anthropic' or 'gemini'"):
        LLMClient.from_env()


def test_blank_model_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_MODEL", "   ")

    with pytest.raises(ConfigurationError, match="LLM_MODEL"):
        LLMClient.from_env()


@pytest.mark.parametrize(
    ("variable_name", "value"),
    [
        ("LLM_TIMEOUT_SECONDS", "not-a-float"),
        ("LLM_MAX_RETRIES", "not-an-int"),
        ("LLM_MAX_OUTPUT_TOKENS", "not-an-int"),
        ("LLM_TEMPERATURE", "not-a-float"),
        ("LLM_VALIDATION_ATTEMPTS", "not-an-int"),
    ],
)
def test_invalid_numeric_environment_value_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    variable_name: str,
    value: str,
) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv(variable_name, value)
    monkeypatch.setattr(llm_client_module, "GeminiProvider", CapturingProvider)

    with pytest.raises(ValueError):
        LLMClient.from_env()


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ],
)
def test_fallback_boolean_environment_values(
    monkeypatch: pytest.MonkeyPatch,
    raw_value: str,
    expected: bool,
) -> None:
    clear_llm_env(monkeypatch)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_FALLBACK_ON_ERROR", raw_value)
    monkeypatch.setattr(llm_client_module, "GeminiProvider", CapturingProvider)

    client = LLMClient.from_env()

    assert client.fallback_on_error is expected
