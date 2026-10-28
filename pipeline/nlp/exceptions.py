"""Custom exceptions used by the NLP module."""


class NLPError(Exception):
    """Base exception for all NLP module errors."""


class ConfigurationError(NLPError):
    """Raised when the NLP module configuration is invalid."""


class LLMGenerationError(NLPError):
    """Raised when the LLM fails to generate valid feedback."""


class UnsupportedViolationError(NLPError):
    """Raised when no prompt exists for a violation type."""

class DiagramRenderError(RuntimeError):
    """Raised when a PlantUML source string fails to render."""