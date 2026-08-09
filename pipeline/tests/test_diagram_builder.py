"""Unit tests for deterministic diagram generation.

These do not require a running PlantUML server - they test that valid
PlantUML source is produced from a trace, and that annotation filtering
correctly drops step numbers that don't exist in the trace. Rendering
against a live server belongs in a separate, network-gated test, the
same way test_live_smoke.py gates the real LLM call.
"""

from __future__ import annotations

from pipeline.nlp.diagram_builder import build_execution_diagram, filter_valid_annotations
from pipeline.nlp.schemas import Counterexample, StepAnnotation

SAMPLE_PARSER_OUTPUT = {
    "verification_result": "FAILED",
    "file": "submission.cpp",
    "line": 7,
    "function": "main",
    "violation_type": "array bounds violated",
    "violation_description": "array upper bound violated",
    "states": [
        {"state_number": 1, "line": 5, "function": "main", "assignment": "i = 5"},
        {"state_number": 2, "line": 7, "function": "main", "assignment": "values[i] = 5"},
    ],
}


def _counterexample() -> Counterexample:
    return Counterexample.model_validate(SAMPLE_PARSER_OUTPUT)


def test_diagram_includes_start_and_stop() -> None:
    diagram = build_execution_diagram(_counterexample())
    assert diagram.startswith("@startuml")
    assert diagram.rstrip().endswith("@enduml")
    assert "start" in diagram
    assert "stop" in diagram


def test_diagram_includes_each_trace_step() -> None:
    counterexample = _counterexample()
    diagram = build_execution_diagram(counterexample)
    for step in counterexample.trace:
        assert ("line %d" % step.line) in diagram


def test_diagram_includes_violation_message() -> None:
    counterexample = _counterexample()
    diagram = build_execution_diagram(counterexample)
    assert "VIOLATION" in diagram


def test_valid_annotation_is_included_as_a_note() -> None:
    counterexample = _counterexample()
    annotations = [StepAnnotation(step=1, note="index reaches its final value here")]
    diagram = build_execution_diagram(counterexample, annotations)
    assert "index reaches its final value here" in diagram


def test_annotation_referencing_missing_step_is_dropped() -> None:
    counterexample = _counterexample()
    annotations = [
        StepAnnotation(step=1, note="valid annotation"),
        StepAnnotation(step=999, note="hallucinated step, should not appear"),
    ]
    valid = filter_valid_annotations(annotations, counterexample)
    assert [a.step for a in valid] == [1]

    diagram = build_execution_diagram(counterexample, valid)
    assert "hallucinated step" not in diagram


def test_special_characters_in_variable_values_do_not_break_syntax() -> None:
    parser_output = dict(SAMPLE_PARSER_OUTPUT)
    parser_output["states"] = [
        {
            "state_number": 1,
            "line": 5,
            "function": "main",
            "assignment": 'label = "quoted; text\nwith newline"',
        },
    ]
    counterexample = Counterexample.model_validate(parser_output)
    diagram = build_execution_diagram(counterexample)

    # Raw semicolons/newlines inside a label would otherwise terminate
    # the PlantUML statement early or split it across lines.
    for line in diagram.splitlines():
        if line.startswith(":") or line.startswith("note") or line.startswith("#"):
            assert line.count(";") <= 1 or line.rstrip().endswith(";")
