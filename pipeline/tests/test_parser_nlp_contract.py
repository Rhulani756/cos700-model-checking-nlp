"""Contract tests between the parser output and the NLP input schema."""

from __future__ import annotations

from typing import Any, Dict

import pytest
from pydantic import ValidationError

from pipeline.nlp.schemas import Counterexample


@pytest.mark.parametrize(
    ("raw_type", "description", "expected"),
    [
        (
            "array bounds violated",
            "array upper bound violated",
            "array_bounds",
        ),
        (
            "dereference failure",
            "null pointer dereference",
            "null_safety",
        ),
        (
            "unwinding assertion",
            "loop bound exceeded",
            "loop_termination",
        ),
        (
            "division by zero",
            "divisor is zero",
            "division_by_zero",
        ),
    ],
)
def test_all_parser_violation_types_are_normalized(
    raw_type: str,
    description: str,
    expected: str,
) -> None:
    parser_output = {
        "verification_result": "FAILED",
        "file": "submission.cpp",
        "line": 10,
        "column": 4,
        "function": "main",
        "violation_type": raw_type,
        "violation_description": description,
        "states": [],
    }

    counterexample = Counterexample.model_validate(parser_output)

    assert counterexample.violation_type.value == expected
    assert counterexample.message == description
    assert counterexample.verification_result == "FAILED"


def test_parser_output_is_accepted_directly(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    counterexample = Counterexample.model_validate(parser_array_bounds_output)

    assert counterexample.violation_type.value == "array_bounds"
    assert counterexample.message == "array upper bound violated"
    assert counterexample.file == "submission.cpp"
    assert counterexample.line == 7
    assert counterexample.column == 18
    assert counterexample.function == "main"
    assert len(counterexample.trace) == 2

    first_step = counterexample.trace[0]
    assert first_step.step == 1
    assert first_step.event == "i = 5"
    assert first_step.line == 5
    assert first_step.function == "main"
    assert first_step.variables[0].name == "i"
    assert first_step.variables[0].value == "5"


def test_raw_violation_type_is_preserved_in_metadata(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    counterexample = Counterexample.model_validate(parser_array_bounds_output)

    assert counterexample.metadata["raw_violation_type"] == "array bounds violated"
    assert counterexample.metadata["verification_result"] == "FAILED"


@pytest.mark.parametrize("verification_result", ["SUCCESSFUL", "UNKNOWN", ""])
def test_non_failed_verification_is_rejected(
    verification_result: str,
) -> None:
    parser_output = {
        "verification_result": verification_result,
        "violation_type": "array bounds violated",
        "violation_description": "array upper bound violated",
    }

    with pytest.raises(ValidationError, match="failed verification"):
        Counterexample.model_validate(parser_output)


def test_unsupported_parser_violation_is_rejected() -> None:
    parser_output = {
        "verification_result": "FAILED",
        "violation_type": "unsupported checker property",
        "violation_description": "an unknown property failed",
    }

    with pytest.raises(ValidationError, match="Unsupported violation type"):
        Counterexample.model_validate(parser_output)


def test_parser_empty_terminal_state_is_ignored() -> None:
    parser_output = {
        "verification_result": "FAILED",
        "violation_type": "division by zero",
        "violation_description": "divisor is zero",
        "states": [
            {
                "state_number": 1,
                "line": 8,
                "function": "divide",
                "assignment": "denominator = 0",
            },
            {},
        ],
    }

    counterexample = Counterexample.model_validate(parser_output)

    assert len(counterexample.trace) == 1
    assert counterexample.trace[0].event == "denominator = 0"


def test_parser_state_without_assignment_remains_useful() -> None:
    parser_output = {
        "verification_result": "FAILED",
        "violation_type": "unwinding assertion",
        "violation_description": "loop bound exceeded",
        "states": [
            {
                "state_number": 4,
                "line": 12,
                "function": "main",
                "assignment": None,
            }
        ],
    }

    counterexample = Counterexample.model_validate(parser_output)

    assert len(counterexample.trace) == 1
    assert counterexample.trace[0].step == 4
    assert counterexample.trace[0].event == "Program state reached"
    assert counterexample.trace[0].variables == []


def test_parser_states_that_are_not_a_list_become_empty_trace() -> None:
    parser_output = {
        "verification_result": "FAILED",
        "violation_type": "null pointer dereference",
        "violation_description": "pointer is null",
        "states": "not-a-list",
    }

    counterexample = Counterexample.model_validate(parser_output)

    assert counterexample.trace == []
