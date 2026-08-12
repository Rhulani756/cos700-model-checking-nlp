"""Optional live API smoke tests.

These tests are skipped by default so normal test runs do not consume API quota.

Run explicitly with:

    RUN_LIVE_NLP_TEST=1 LLM_INCLUDE_DIAGRAM=true \
    python -m pytest pipeline/tests/test_live_smoke.py -q -s
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import pytest

from pipeline.nlp.llm_client import LLMClient


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_NLP_TEST") != "1",
    reason="Set RUN_LIVE_NLP_TEST=1 to call the configured LLM API.",
)


REPORT_DIR = Path("reports") / "test_diagrams"


def _diagram_enabled() -> bool:
    return os.getenv(
        "LLM_INCLUDE_DIAGRAM",
        "true",
    ).strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _save_svg(case_name: str, svg: str) -> None:
    if not svg:
        return

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = REPORT_DIR / ("%s.svg" % case_name)

    output_path.write_text(
        svg,
        encoding="utf-8",
    )

    print("\nSaved diagram:", output_path)


def _assert_valid_result(
    case_name: str,
    result: Any,
) -> None:
    print("\n")
    print("=" * 80)
    print("CASE:", case_name)
    print("=" * 80)

    print("\n=== FEEDBACK ===")
    print(result.feedback.model_dump_json(indent=2))

    print("\n=== DIAGRAM STATUS ===")
    print("PlantUML generated:", bool(result.diagram_plantuml))
    print("SVG generated:", bool(result.diagram_svg))
    print("Render error:", result.diagram_render_error)
    print("PlantUML length:", len(result.diagram_plantuml))
    print("SVG length:", len(result.diagram_svg))

    assert result.used_fallback is False

    assert result.feedback.title
    assert result.feedback.summary
    assert result.feedback.root_cause
    assert result.feedback.evidence
    assert result.feedback.execution_path
    assert result.feedback.why_it_matters
    assert result.feedback.suggested_changes
    assert result.feedback.check_your_understanding
    assert result.feedback.confidence in {
        "high",
        "medium",
        "low",
    }

    if _diagram_enabled():
        assert result.diagram_plantuml
        assert result.diagram_svg
        assert not result.diagram_render_error

        _save_svg(
            case_name,
            result.diagram_svg,
        )


TEST_CASES = [
    (
        "array_bounds",
        {
            "verification_result": "FAILED",
            "file": "array_bounds.cpp",
            "line": 7,
            "column": 18,
            "function": "main",
            "violation_type": "array bounds violated",
            "violation_description": "array upper bound violated",
            "source_snippet": """
int main() {
    int values[5] = {0};
    int i = 5;
    values[i] = 5;
    return 0;
}
""",
            "states": [
                {
                    "state_number": 1,
                    "line": 5,
                    "function": "main",
                    "assignment": "i = 5",
                },
                {
                    "state_number": 2,
                    "line": 7,
                    "function": "main",
                    "assignment": "values[i] = 5",
                },
            ],
        },
    ),
    (
        "division_by_zero",
        {
            "verification_result": "FAILED",
            "file": "division_by_zero.cpp",
            "line": 7,
            "column": 18,
            "function": "main",
            "violation_type": "division by zero",
            "violation_description": "division by zero",
            "source_snippet": """
int main() {
    int total = 20;
    int count = 0;
    int average = total / count;
    return 0;
}
""",
            "states": [
                {
                    "state_number": 1,
                    "line": 3,
                    "function": "main",
                    "assignment": "total = 20",
                },
                {
                    "state_number": 2,
                    "line": 4,
                    "function": "main",
                    "assignment": "count = 0",
                },
                {
                    "state_number": 3,
                    "line": 5,
                    "function": "main",
                    "assignment": "average = total / count",
                },
            ],
        },
    ),
    (
        "null_safety",
        {
            "verification_result": "FAILED",
            "file": "null_pointer.cpp",
            "line": 4,
            "column": 18,
            "function": "main",
            "violation_type": "null pointer dereference",
            "violation_description": "dereference failure: pointer is null",
            "source_snippet": """
int main() {
    int *value = 0;
    int result = *value;
    return 0;
}
""",
            "states": [
                {
                    "state_number": 1,
                    "line": 2,
                    "function": "main",
                    "assignment": "value = NULL",
                },
                {
                    "state_number": 2,
                    "line": 3,
                    "function": "main",
                    "assignment": "result = *value",
                },
            ],
        },
    ),
    (
        "loop_termination",
        {
            "verification_result": "FAILED",
            "file": "infinite_loop.cpp",
            "line": 4,
            "column": 5,
            "function": "main",
            "violation_type": "unwinding assertion",
            "violation_description": "unwinding assertion loop.0 failed",
            "source_snippet": """
int main() {
    int i = 0;

    while (i < 10) {
        i = 0;
    }

    return 0;
}
""",
            "states": [
                {
                    "state_number": 1,
                    "line": 2,
                    "function": "main",
                    "assignment": "i = 0",
                },
                {
                    "state_number": 2,
                    "line": 4,
                    "function": "main",
                    "assignment": "i = 0",
                },
                {
                    "state_number": 3,
                    "line": 5,
                    "function": "main",
                    "assignment": "i = 0",
                },
            ],
            "metadata": {
                "unwind_bound": 10,
            },
        },
    ),
]


@pytest.mark.parametrize(
    "case_name,parser_output",
    TEST_CASES,
    ids=[case[0] for case in TEST_CASES],
)
def test_live_feedback_generation(
    case_name: str,
    parser_output: Dict[str, Any],
) -> None:
    client = LLMClient.from_env()

    result = client.generate_feedback_sync(
        parser_output
    )

    _assert_valid_result(
        case_name,
        result,
    )


def test_live_canonical_trace_format() -> None:
    """Confirm canonical trace input works as well as parser-native states."""

    parser_output = {
        "verification_result": "FAILED",
        "tool": "esbmc",
        "file": "canonical_div_zero.cpp",
        "line": 5,
        "function": "main",
        "violation_type": "division_by_zero",
        "message": "division by zero",
        "source_snippet": """
int main() {
    int total = 10;
    int count = 0;
    int result = total / count;
}
""",
        "trace": [
            {
                "step": 1,
                "event": "count becomes zero",
                "file": "canonical_div_zero.cpp",
                "line": 3,
                "function": "main",
                "variables": {
                    "count": 0,
                },
            },
            {
                "step": 2,
                "event": "division evaluated with zero divisor",
                "file": "canonical_div_zero.cpp",
                "line": 4,
                "function": "main",
                "variables": {
                    "total": 10,
                    "count": 0,
                },
            },
        ],
    }

    client = LLMClient.from_env()

    result = client.generate_feedback_sync(
        parser_output
    )

    _assert_valid_result(
        "canonical_trace_format",
        result,
    )


def _build_large_parser_output(
    trace_size: int,
) -> Dict[str, Any]:
    states = []

    for state_number in range(1, trace_size + 1):
        states.append(
            {
                "state_number": state_number,
                "line": 5,
                "function": "main",
                "assignment": "i = %d" % state_number,
            }
        )

    states.append(
        {
            "state_number": trace_size + 1,
            "line": 9,
            "function": "main",
            "assignment": "values[i] = 5",
        }
    )

    return {
        "verification_result": "FAILED",
        "file": "large_trace.cpp",
        "line": 9,
        "column": 5,
        "function": "main",
        "violation_type": "array bounds violated",
        "violation_description": "array upper bound violated",
        "source_snippet": """
int main() {
    int values[5] = {0};
    int i = 0;

    while (i < 1000) {
        ++i;
    }

    values[i] = 5;
    return 0;
}
""",
        "states": states,
    }


@pytest.mark.parametrize(
    "trace_size",
    [
        10,
        25,
        50,
        67,
        100,
        150,
        250,
        500,
    ],
)
def test_live_large_trace(
    trace_size: int,
) -> None:
    client = LLMClient.from_env()

    parser_output = _build_large_parser_output(
        trace_size
    )

    result = client.generate_feedback_sync(
        parser_output
    )

    case_name = "large_trace_%d" % trace_size

    print("\n")
    print("=" * 80)
    print("TRACE SIZE:", trace_size)
    print("=" * 80)

    _assert_valid_result(
        case_name,
        result,
    )