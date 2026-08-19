"""Unit tests for NLP input and output Pydantic schemas."""

from __future__ import annotations

from typing import Any, Dict

import pytest
from pydantic import ValidationError

from pipeline.nlp.schemas import (
    Counterexample,
    PedagogicalFeedback,
    TraceStep,
    TraceVariable,
    ViolationType,
    normalize_violation_type,
)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("array_bounds", ViolationType.ARRAY_BOUNDS),
        ("array-out-of-bounds", ViolationType.ARRAY_BOUNDS),
        ("null pointer", ViolationType.NULL_SAFETY),
        ("loop_unwinding", ViolationType.LOOP_TERMINATION),
        ("divide-by-zero", ViolationType.DIVISION_BY_ZERO),
    ],
)
def test_normalize_violation_aliases(
    raw_value: str,
    expected: ViolationType,
) -> None:
    assert normalize_violation_type(raw_value) == expected


def test_trace_variable_coerces_values_to_strings() -> None:
    variable = TraceVariable.model_validate(
        {"name": "count", "value": 7, "type": "int"}
    )

    assert variable.name == "count"
    assert variable.value == "7"
    assert variable.data_type == "int"


def test_trace_step_accepts_variable_mapping() -> None:
    step = TraceStep.model_validate(
        {
            "state_number": "3",
            "assignment": "denominator = 0",
            "line_number": "11",
            "function_name": "divide",
            "variables": {"denominator": 0, "numerator": 10},
        }
    )

    assert step.step == 3
    assert step.event == "denominator = 0"
    assert step.line == 11
    assert step.function == "divide"
    assert [(item.name, item.value) for item in step.variables] == [
        ("denominator", "0"),
        ("numerator", "10"),
    ]


def test_counterexample_accepts_canonical_input() -> None:
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "division_by_zero",
            "message": "The denominator is zero.",
            "tool": "cbmc",
            "source_file": "program.cpp",
            "line_number": 20,
            "function_name": "average",
            "code_snippet": "return total / count;",
            "trace": [
                {
                    "step": 1,
                    "event": "count = 0",
                    "variables": {"count": 0},
                }
            ],
        }
    )

    assert counterexample.violation_type is ViolationType.DIVISION_BY_ZERO
    assert counterexample.tool == "cbmc"
    assert counterexample.file == "program.cpp"
    assert counterexample.line == 20
    assert counterexample.function == "average"
    assert counterexample.source_snippet == "return total / count;"
    assert counterexample.trace[0].variables[0].value == "0"


def test_unknown_model_checker_is_normalized_to_unknown() -> None:
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "division by zero",
            "violation_description": "divisor is zero",
            "tool": "other-checker",
        }
    )

    assert counterexample.tool == "unknown"


def test_invalid_line_and_column_are_discarded() -> None:
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "array bounds violated",
            "violation_description": "upper bound violated",
            "line": 0,
            "column": "not-a-number",
        }
    )

    assert counterexample.line is None
    assert counterexample.column is None


def test_valid_pedagogical_feedback_is_accepted(
    valid_feedback_dict: Dict[str, Any],
) -> None:
    feedback = PedagogicalFeedback.model_validate(valid_feedback_dict)

    assert feedback.confidence == "high"
    assert len(feedback.evidence) == 2
    assert len(feedback.suggested_changes) == 2


@pytest.mark.parametrize(
    "field_name",
    ["title", "summary", "root_cause", "why_it_matters", "check_your_understanding"],
)
def test_blank_required_feedback_text_is_rejected(
    valid_feedback_dict: Dict[str, Any],
    field_name: str,
) -> None:
    invalid = dict(valid_feedback_dict)
    invalid[field_name] = "   "

    with pytest.raises(ValidationError, match="may not be blank"):
        PedagogicalFeedback.model_validate(invalid)


@pytest.mark.parametrize(
    "field_name",
    ["evidence", "execution_path", "suggested_changes"],
)
def test_empty_feedback_lists_are_rejected(
    valid_feedback_dict: Dict[str, Any],
    field_name: str,
) -> None:
    invalid = dict(valid_feedback_dict)
    invalid[field_name] = ["", "   "]

    with pytest.raises(ValidationError, match="at least one item"):
        PedagogicalFeedback.model_validate(invalid)


def test_invalid_confidence_is_rejected(
    valid_feedback_dict: Dict[str, Any],
) -> None:
    invalid = dict(valid_feedback_dict)
    invalid["confidence"] = "certain"

    with pytest.raises(ValidationError):
        PedagogicalFeedback.model_validate(invalid)


def test_extra_generated_field_is_rejected(
    valid_feedback_dict: Dict[str, Any],
) -> None:
    invalid = dict(valid_feedback_dict)
    invalid["unsupported_field"] = "unexpected"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        PedagogicalFeedback.model_validate(invalid)
