"""Shared pytest configuration and fixtures for the NLP module tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import pytest


# Makes imports work with both:
#   pytest tests -q
#   python -m pytest tests -q
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def valid_feedback_dict() -> Dict[str, Any]:
    """Return a complete response accepted by PedagogicalFeedback."""

    return {
        "title": "Array index exceeds its valid range",
        "summary": "The loop reaches an index that is outside the array.",
        "root_cause": "The loop condition allows the index to equal the array size.",
        "evidence": [
            "The checker reports the violation at submission.cpp line 7.",
            "The final trace records i=5.",
        ],
        "execution_path": [
            "The index starts at 0.",
            "The loop increments the index until it becomes 5.",
            "The program then accesses values[5].",
        ],
        "why_it_matters": "An array of size 5 only has indices 0 through 4.",
        "suggested_changes": [
            "Use an exclusive upper bound in the loop condition.",
            "Validate the index before accessing the array.",
        ],
        "example_fix": "for (int i = 0; i < 5; ++i) { values[i] = i; }",
        "check_your_understanding": "What is the largest valid index of an array with five elements?",
        "confidence": "high",
    }


@pytest.fixture
def parser_array_bounds_output() -> Dict[str, Any]:
    """Return representative output from the team's parser implementation."""

    return {
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
