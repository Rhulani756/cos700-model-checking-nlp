"""Validated input and output schemas for pedagogical feedback generation."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ViolationType(str, Enum):
    ARRAY_BOUNDS = "array_bounds"
    NULL_SAFETY = "null_safety"
    LOOP_TERMINATION = "loop_termination"
    DIVISION_BY_ZERO = "division_by_zero"


_VIOLATION_ALIASES = {
    "array_bounds": ViolationType.ARRAY_BOUNDS,
    "array_bound": ViolationType.ARRAY_BOUNDS,
    "bounds": ViolationType.ARRAY_BOUNDS,
    "out_of_bounds": ViolationType.ARRAY_BOUNDS,
    "array_out_of_bounds": ViolationType.ARRAY_BOUNDS,
    "buffer_overflow": ViolationType.ARRAY_BOUNDS,
    "null_safety": ViolationType.NULL_SAFETY,
    "null_pointer": ViolationType.NULL_SAFETY,
    "null_dereference": ViolationType.NULL_SAFETY,
    "nullptr_dereference": ViolationType.NULL_SAFETY,
    "pointer_dereference": ViolationType.NULL_SAFETY,
    "loop_termination": ViolationType.LOOP_TERMINATION,
    "termination": ViolationType.LOOP_TERMINATION,
    "non_termination": ViolationType.LOOP_TERMINATION,
    "unwinding_assertion": ViolationType.LOOP_TERMINATION,
    "loop_unwinding": ViolationType.LOOP_TERMINATION,
    "division_by_zero": ViolationType.DIVISION_BY_ZERO,
    "divide_by_zero": ViolationType.DIVISION_BY_ZERO,
    "div_by_zero": ViolationType.DIVISION_BY_ZERO,
    "zero_division": ViolationType.DIVISION_BY_ZERO,
}


def normalize_violation_type(
    value: Any,
    description: Any = None,
) -> ViolationType:
    """Map canonical values and checker-specific labels to one category."""

    if isinstance(value, ViolationType):
        return value

    raw_value = str(value or "").strip().lower()
    normalized = raw_value.replace("-", "_").replace(" ", "_")

    if normalized in _VIOLATION_ALIASES:
        return _VIOLATION_ALIASES[normalized]

    combined = "%s %s" % (raw_value, str(description or "").strip().lower())

    if any(
        phrase in combined
        for phrase in (
            "array bounds",
            "array bound",
            "out of bounds",
            "out-of-bounds",
            "upper bound",
            "lower bound",
            "buffer overflow",
        )
    ):
        return ViolationType.ARRAY_BOUNDS

    if any(
        phrase in combined
        for phrase in (
            "null pointer",
            "null dereference",
            "nullptr",
            "invalid pointer",
            "pointer dereference",
            "dereference failure",
        )
    ):
        return ViolationType.NULL_SAFETY

    if any(
        phrase in combined
        for phrase in (
            "unwinding assertion",
            "unwind",
            "loop termination",
            "non-termination",
            "nontermination",
            "loop bound",
        )
    ):
        return ViolationType.LOOP_TERMINATION

    if any(
        phrase in combined
        for phrase in (
            "division by zero",
            "divide by zero",
            "division-by-zero",
            "zero divisor",
            "divisor is zero",
        )
    ):
        return ViolationType.DIVISION_BY_ZERO

    raise ValueError("Unsupported violation type: %r" % value)


def _positive_int_or_none(value: Any) -> Optional[int]:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None

    return number if number >= 1 else None


def _step_number(value: Any, fallback: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return fallback

    return number if number >= 0 else fallback


def _extract_assignment_variables(assignment: Any) -> List[Dict[str, str]]:
    """Extract a simple name/value pair from an ESBMC assignment line."""

    if assignment is None:
        return []

    assignment_text = str(assignment).strip()
    if "=" not in assignment_text:
        return []

    name, value = assignment_text.split("=", 1)
    name = name.strip()
    value = value.strip()

    if not name:
        return []

    return [{"name": name, "value": value, "data_type": ""}]


def _convert_parser_states(
    states: Any,
    default_file: str,
) -> List[Dict[str, Any]]:
    """Convert the parser's states list into the canonical trace format."""

    if not isinstance(states, list):
        return []

    trace: List[Dict[str, Any]] = []

    for index, state in enumerate(states):
        if not isinstance(state, dict):
            continue

        assignment = state.get("assignment")
        state_number = state.get("state_number")

        # The parser can append an empty entry when it reaches
        # the "Violated property" section. Ignore that entry.
        if assignment is None and state_number is None:
            continue

        event = (
            str(assignment).strip()
            if assignment is not None and str(assignment).strip()
            else "Program state reached"
        )

        trace.append(
            {
                "step": _step_number(state_number, index + 1),
                "event": event,
                "file": str(state.get("file", default_file) or ""),
                "line": _positive_int_or_none(state.get("line")),
                "function": str(state.get("function", "") or ""),
                "thread": str(state.get("thread", "") or ""),
                "variables": _extract_assignment_variables(assignment),
            }
        )

    return trace


class TraceVariable(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1)
    value: str = ""
    data_type: str = ""

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if isinstance(value, dict):
            data = dict(value)
            if "data_type" not in data:
                data["data_type"] = data.get("type", "")
            data["name"] = str(data.get("name", ""))
            data["value"] = str(data.get("value", ""))
            data["data_type"] = str(data.get("data_type", ""))
            return data
        return value


class TraceStep(BaseModel):
    model_config = ConfigDict(extra="ignore")

    step: int = Field(ge=0)
    event: str = Field(min_length=1)
    file: str = ""
    line: Optional[int] = Field(default=None, ge=1)
    function: str = ""
    thread: str = ""
    variables: List[TraceVariable] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def normalize_input(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = dict(value)
        assignment = data.get("assignment")

        data.setdefault(
            "step",
            data.get("state_number", data.get("step_number", data.get("index", 0))),
        )
        data.setdefault(
            "event",
            data.get(
                "description",
                data.get(
                    "action",
                    data.get(
                        "kind",
                        assignment if assignment is not None else "Program state reached",
                    ),
                ),
            ),
        )
        data.setdefault("file", data.get("source_file", data.get("filename", "")))
        data.setdefault("line", data.get("line_number"))
        data.setdefault("function", data.get("function_name", ""))
        data.setdefault("thread", data.get("thread_id", ""))

        data["step"] = _step_number(data.get("step"), 0)
        data["event"] = str(data.get("event", "Program state reached") or "Program state reached")
        data["file"] = str(data.get("file", "") or "")
        data["line"] = _positive_int_or_none(data.get("line"))
        data["function"] = str(data.get("function", "") or "")
        data["thread"] = str(data.get("thread", "") or "")

        variables = data.get("variables")
        if variables is None and assignment is not None:
            variables = _extract_assignment_variables(assignment)

        if isinstance(variables, dict):
            variables = [
                {"name": str(name), "value": str(variable_value)}
                for name, variable_value in variables.items()
            ]

        data["variables"] = variables or []
        return data


class Counterexample(BaseModel):
    """Parser output consumed directly by the NLP module.

    This model accepts the parser's fields:
    ``verification_result``, ``violation_description`` and ``states``.
    It normalizes them internally to ``message`` and ``trace`` for prompting.
    """

    model_config = ConfigDict(extra="allow")

    violation_type: ViolationType
    verification_result: str = "FAILED"
    tool: Literal["cbmc", "esbmc", "unknown"] = "unknown"
    property_id: str = ""
    message: str = Field(min_length=1)
    file: str = ""
    line: Optional[int] = Field(default=None, ge=1)
    column: Optional[int] = Field(default=None, ge=1)
    function: str = ""
    source_snippet: str = ""
    trace: List[TraceStep] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def normalize_parser_output(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value

        data = dict(value)

        verification_result = str(
            data.get("verification_result", "FAILED")
        ).strip().upper()

        if verification_result != "FAILED":
            raise ValueError(
                "NLP feedback can only be generated for failed verification cases. "
                "Received: %s" % (verification_result or "missing result")
            )

        raw_violation_type = data.get(
            "violation_type",
            data.get("property_type", data.get("error_type", data.get("property"))),
        )
        violation_description = data.get(
            "violation_description",
            data.get("description", data.get("failure_message", data.get("reason"))),
        )

        data["verification_result"] = verification_result
        data["violation_type"] = normalize_violation_type(
            raw_violation_type,
            violation_description,
        )
        data["property_id"] = str(
            data.get("property_id", data.get("property_name", data.get("propertyId", "")))
            or ""
        )

        message = data.get("message") or violation_description or raw_violation_type
        data["message"] = str(message or "The model checker found a logical error.").strip()

        data["file"] = str(
            data.get("file", data.get("source_file", data.get("filename", ""))) or ""
        )
        data["line"] = _positive_int_or_none(
            data.get("line", data.get("line_number"))
        )
        data["column"] = _positive_int_or_none(data.get("column"))
        data["function"] = str(
            data.get("function", data.get("function_name", "")) or ""
        )
        data["source_snippet"] = str(
            data.get("source_snippet", data.get("code_snippet", data.get("source", "")))
            or ""
        )

        if "trace" not in data:
            if "states" in data:
                data["trace"] = _convert_parser_states(
                    data.get("states"),
                    default_file=data["file"],
                )
            else:
                data["trace"] = data.get("counterexample", data.get("steps", []))

        tool = str(data.get("tool", data.get("model_checker", "unknown"))).lower()
        data["tool"] = tool if tool in {"cbmc", "esbmc"} else "unknown"

        metadata = data.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}
        metadata.setdefault("raw_violation_type", str(raw_violation_type or ""))
        metadata.setdefault("verification_result", verification_result)
        data["metadata"] = metadata

        return data

    @field_validator("violation_type", mode="before")
    @classmethod
    def validate_violation_type(cls, value: Any) -> ViolationType:
        return normalize_violation_type(value)


class PedagogicalFeedback(BaseModel):
    """Structured feedback returned to the formatter and API layer."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(description="Short, specific name for the logical error.")
    summary: str = Field(description="One or two novice-friendly sentences describing the failure.")
    root_cause: str = Field(description="The direct logical cause supported by the counterexample.")
    evidence: List[str] = Field(
        description="Concrete facts from the trace, such as line numbers and variable values."
    )
    execution_path: List[str] = Field(
        description="A short chronological explanation of how execution reaches the violation."
    )
    why_it_matters: str = Field(
        description="The relevant programming concept and the consequence of the error."
    )
    suggested_changes: List[str] = Field(
        description="Actionable changes that guide the student without replacing the assignment."
    )
    example_fix: str = Field(
        description="A minimal C++ illustration, or an empty string if the trace is insufficient."
    )
    check_your_understanding: str = Field(
        description="One question that helps the student verify their understanding."
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence based only on the evidence available in the counterexample."
    )

    @field_validator(
        "title",
        "summary",
        "root_cause",
        "why_it_matters",
        "check_your_understanding",
    )
    @classmethod
    def reject_blank_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Feedback fields may not be blank")
        return value

    @field_validator("evidence", "execution_path", "suggested_changes")
    @classmethod
    def reject_empty_lists(cls, value: List[str]) -> List[str]:
        cleaned = [item.strip() for item in value if item and item.strip()]
        if not cleaned:
            raise ValueError("Feedback lists must contain at least one item")
        return cleaned


class FeedbackGenerationResult(BaseModel):
    """Feedback plus generation metadata that should not be model-generated."""

    feedback: PedagogicalFeedback
    provider: str
    model: str
    prompt_version: str
    used_fallback: bool = False
    latency_ms: int = Field(ge=0)
