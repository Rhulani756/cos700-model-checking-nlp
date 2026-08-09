"""Deterministic PlantUML generation from a verified counterexample trace.

This module never calls an LLM. The diagram is a direct rendering of
``Counterexample.trace``, which is already validated by ``schemas.py``.
Keeping diagram generation deterministic avoids the failure mode observed
when asking an LLM to author PlantUML syntax directly: a model can produce
diagram code that renders fine most of the time and fails unpredictably
otherwise, and syntax errors surface only at render time, not at the
point where the response is generated.

The only LLM-authored content that reaches the diagram is
``StepAnnotation.note`` — short text spliced into a template, never
PlantUML syntax the LLM writes itself.
"""

from __future__ import annotations

from typing import Dict, Iterable, List

from .schemas import Counterexample, StepAnnotation, TraceStep, ViolationType

_DIAGRAM_TITLES: Dict[ViolationType, str] = {
    ViolationType.ARRAY_BOUNDS: "Execution Path - Array Bounds Violation",
    ViolationType.NULL_SAFETY: "Execution Path - Null Pointer Dereference",
    ViolationType.LOOP_TERMINATION: "Execution Path - Loop Termination",
    ViolationType.DIVISION_BY_ZERO: "Execution Path - Division by Zero",
}

_MAX_NOTE_LENGTH = 160
_MAX_LABEL_LENGTH = 120


def build_execution_diagram(
    counterexample: Counterexample,
    annotations: Iterable[StepAnnotation] = (),
) -> str:
    """Build a PlantUML activity diagram from a counterexample's trace.

    Only steps present in ``counterexample.trace`` are rendered. Any
    ``StepAnnotation`` whose ``step`` does not match a real trace step is
    silently dropped by ``filter_valid_annotations`` before this is
    called — this function assumes it has already been filtered.
    """

    annotations_by_step = {annotation.step: annotation.note for annotation in annotations}

    title = _DIAGRAM_TITLES.get(
        counterexample.violation_type, "Execution Path - Verification Failure"
    )

    lines: List[str] = [
        "@startuml",
        "skinparam defaultFontName Monospaced",
        "skinparam ActivityBackgroundColor #FFFBE6",
        "skinparam ActivityBorderColor #8A8A8A",
        "skinparam NoteBackgroundColor #EAF3FF",
        "skinparam NoteBorderColor #6C97C2",
        'title %s' % _escape(title),
        "start",
    ]

    for step in counterexample.trace:
        lines.append(":%s;" % _escape(_step_label(step)))
        note = annotations_by_step.get(step.step)
        if note:
            lines.append("note right: %s" % _escape(_truncate(note, _MAX_NOTE_LENGTH)))

    lines.append(
    ":VIOLATION\\n%s;"
    % _escape(_truncate(counterexample.message, _MAX_LABEL_LENGTH))
    )
    lines.append("stop")
    lines.append("@enduml")

    return "\n".join(lines)


def filter_valid_annotations(
    annotations: Iterable[StepAnnotation],
    counterexample: Counterexample,
) -> List[StepAnnotation]:
    """Drop any annotation that doesn't reference a real trace step.

    The LLM can hallucinate a step number the same way it can hallucinate
    anything else. Since annotations only ever contribute text (never
    diagram syntax), an invalid one is simply omitted rather than treated
    as an error worth failing the whole response over.
    """

    valid_steps = {step.step for step in counterexample.trace}
    return [annotation for annotation in annotations if annotation.step in valid_steps]


def _step_label(step: TraceStep) -> str:
    location = "line %d" % step.line if step.line else step.function or "unknown location"
    if step.variables:
        assignments = ", ".join(
            "%s = %s" % (variable.name, _truncate(variable.value, 40))
            for variable in step.variables
        )
        return _truncate("%s: %s" % (location, assignments), _MAX_LABEL_LENGTH)
    return _truncate("%s: %s" % (location, step.event), _MAX_LABEL_LENGTH)


def _truncate(text: str, limit: int) -> str:
    text = text or ""
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "\u2026"


def _escape(text: str) -> str:
    """Escape characters that would otherwise break PlantUML syntax.

    Applies to any text embedded in a diagram label, note, or title —
    including trace variable values and violation messages, which
    originate from the checker output and are not guaranteed to be
    free of quotes, semicolons, or newlines.
    """

    return (
        (text or "")
        .replace("\\", "\\\\")
        .replace('"', "'")
        .replace(";", ",")
        .replace("\n", " ")
        .replace("\r", " ")
    )
