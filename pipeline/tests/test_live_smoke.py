"""Optional live API smoke test.

This file is skipped by default so normal test runs do not consume API quota.
Run it explicitly with:

    RUN_LIVE_NLP_TEST=1 python -m pytest pipeline/tests/test_live_smoke.py -q -s
"""

from __future__ import annotations

import os
from xmlrpc import client

import pytest

from pipeline.nlp.llm_client import LLMClient


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_NLP_TEST") != "1",
    reason="Set RUN_LIVE_NLP_TEST=1 to call the configured LLM API.",
)


def test_live_feedback_generation() -> None:
    parser_output = {
        "verification_result": "FAILED",
        "file": "submission.cpp",
        "line": 7,
        "column": 18,
        "function": "main",
        "violation_type": "array bounds violated",
        "violation_description": "array upper bound violated",
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
    }

    client = LLMClient.from_env()
    result = client.generate_feedback_sync(parser_output)

    print("\n=== FEEDBACK ===")
    print(result.feedback.model_dump_json(indent=2))

    print("\n=== PLANTUML ===")
    print(result.diagram_plantuml)

    print("\n=== SVG ===")
    print(result.diagram_svg)

    print("\n=== DIAGRAM ERROR ===")
    print(result.diagram_render_error)

    assert result.used_fallback is False
    assert result.feedback.title
    assert result.feedback.root_cause
    assert result.feedback.evidence
    assert result.diagram_plantuml
    assert result.diagram_svg
    assert not result.diagram_render_error
