"""Tests for property prompt selection and prompt compaction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pytest

from pipeline.nlp.exceptions import UnsupportedViolationError
from pipeline.nlp.prompt_builder import PROMPT_VERSION, SYSTEM_PROMPT, PromptBuilder
from pipeline.nlp.schemas import Counterexample, ViolationType


EXPECTED_GUIDANCE = {
    "array_bounds": "valid indices 0 through N - 1",
    "null_safety": "pointer that is dereferenced without being proven valid",
    "loop_termination": "configured unwind bound",
    "division_by_zero": "expression used as the divisor",
}


@pytest.mark.parametrize(
    ("violation_type", "description"),
    [
        ("array bounds violated", "array upper bound violated"),
        ("null pointer dereference", "pointer is null"),
        ("unwinding assertion", "loop bound exceeded"),
        ("division by zero", "divisor is zero"),
    ],
)
def test_each_property_prompt_is_loaded_into_user_prompt(
    violation_type: str,
    description: str,
) -> None:
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": violation_type,
            "violation_description": description,
        }
    )

    system_prompt, user_prompt = PromptBuilder().build(counterexample)

    expected = EXPECTED_GUIDANCE[counterexample.violation_type.value]
    assert expected in user_prompt
    assert system_prompt == SYSTEM_PROMPT
    assert counterexample.violation_type.value in user_prompt


def test_only_selected_property_guidance_is_present() -> None:
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "array bounds violated",
            "violation_description": "array upper bound violated",
        }
    )

    _, user_prompt = PromptBuilder().build(counterexample)

    assert EXPECTED_GUIDANCE["array_bounds"] in user_prompt
    assert EXPECTED_GUIDANCE["null_safety"] not in user_prompt
    assert EXPECTED_GUIDANCE["loop_termination"] not in user_prompt
    assert EXPECTED_GUIDANCE["division_by_zero"] not in user_prompt


def test_missing_prompt_file_raises_clear_error(tmp_path: Path) -> None:
    builder = PromptBuilder(prompts_directory=tmp_path)
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "array_bounds",
            "message": "array upper bound violated",
        }
    )

    with pytest.raises(UnsupportedViolationError, match="No prompt template found"):
        builder.build(counterexample)


def test_empty_prompt_file_raises_clear_error(tmp_path: Path) -> None:
    (tmp_path / "array_bounds.txt").write_text("   \n", encoding="utf-8")
    builder = PromptBuilder(prompts_directory=tmp_path)
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "array_bounds",
            "message": "array upper bound violated",
        }
    )

    with pytest.raises(UnsupportedViolationError, match="Prompt template is empty"):
        builder.build(counterexample)


def test_source_snippet_is_truncated() -> None:
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "array_bounds",
            "message": "array upper bound violated",
            "source_snippet": "x" * 50,
        }
    )
    builder = PromptBuilder(max_source_chars=12)

    _, user_prompt = builder.build(counterexample)

    assert "x" * 12 in user_prompt
    assert "[truncated 38 characters]" in user_prompt
    assert "x" * 50 not in user_prompt


def test_trace_selection_preserves_first_and_last_steps() -> None:
    trace = [
        {
            "step": number,
            "event": "state-%d" % number,
            "variables": {"i": number},
        }
        for number in range(20)
    ]
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "loop_termination",
            "message": "loop bound exceeded",
            "trace": trace,
        }
    )
    builder = PromptBuilder(max_trace_steps=8)

    compact = builder._compact_counterexample(counterexample)
    selected_steps = [step["step"] for step in compact["trace"]]

    assert selected_steps == [0, 1, 2, 3, 16, 17, 18, 19]
    assert compact["trace_was_truncated"] is True
    assert compact["total_trace_steps"] == 20


def test_trace_value_is_truncated() -> None:
    counterexample = Counterexample.model_validate(
        {
            "verification_result": "FAILED",
            "violation_type": "division_by_zero",
            "message": "divisor is zero",
            "trace": [
                {
                    "step": 1,
                    "event": "denominator assigned",
                    "variables": {
                        "denominator": "1234567890",
                    },
                }
            ],
        }
    )
    builder = PromptBuilder(max_value_chars=4)

    compact = builder._compact_counterexample(counterexample)

    value = compact["trace"][0]["variables"][0]["value"]
    assert value.startswith("1234")
    assert "[truncated 6 characters]" in value


def test_prompt_contains_machine_readable_counterexample_json(
    parser_array_bounds_output: Dict[str, Any],
) -> None:
    counterexample = Counterexample.model_validate(parser_array_bounds_output)
    _, user_prompt = PromptBuilder().build(counterexample)

    start = user_prompt.index("<counterexample_json>") + len("<counterexample_json>")
    end = user_prompt.index("</counterexample_json>")
    embedded = json.loads(user_prompt[start:end].strip())

    assert embedded["verification_result"] == "FAILED"
    assert embedded["violation_type"] == "array_bounds"
    assert embedded["location"]["line"] == 7
    assert embedded["trace"][0]["event"] == "i = 5"


def test_prompt_version_is_defined() -> None:
    assert PROMPT_VERSION
    assert PROMPT_VERSION.count(".") == 2
