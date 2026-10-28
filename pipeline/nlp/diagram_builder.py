from __future__ import annotations

import os
import re
import textwrap
from typing import Dict, Iterable, List, Optional, Set

from .schemas import Counterexample, StepAnnotation, TraceStep, ViolationType


_DIAGRAM_TITLES: Dict[ViolationType, str] = {
    ViolationType.ARRAY_BOUNDS: "Execution Path - Array Bounds Violation",
    ViolationType.NULL_SAFETY: "Execution Path - Null Pointer Dereference",
    ViolationType.LOOP_TERMINATION: "Execution Path - Loop Termination",
    ViolationType.DIVISION_BY_ZERO: "Execution Path - Division by Zero",
}

_MAX_DISPLAY_STEPS = 4
_MAX_LABEL_LENGTH = 78
_MAX_NOTE_LENGTH = 44
_MAX_ANNOTATIONS = 1

_INTERNAL_TOKENS = (
    "stdin",
    "stdout",
    "stderr",
    "virtual_table",
    "std::",
    "tag-std::",
    "streambuf",
    "seekoff",
    "seekpos",
    "showmanyc",
    "underflow",
    "overflow",
    "__esbmc",
    "__cprover",
    "__gnu_cxx",
    "__cxxabiv1",
    "__static_initialization",
    "__libc",
    "_filesize",
)

_INTERNAL_VARIABLE_NAMES = {
    "stdin",
    "stdout",
    "stderr",
    "goodbit",
    "badbit",
    "failbit",
    "eofbit",
    "_filesize",
}


def build_execution_diagram(
    counterexample: Counterexample,
    annotations: Iterable[StepAnnotation] = (),
) -> str:
    """Build a compact, source-aware PlantUML activity diagram."""

    display_steps = _select_display_steps(counterexample)

    annotations_by_step = {
        annotation.step: annotation.note
        for annotation in annotations
    }

    title = _DIAGRAM_TITLES.get(
        counterexample.violation_type,
        "Execution Path - Verification Failure",
    )

    lines: List[str] = [
        "@startuml",
        "skinparam defaultFontName Monospaced",
        "skinparam ActivityBackgroundColor #FFFBE6",
        "skinparam ActivityBorderColor #8A8A8A",
        "skinparam NoteBackgroundColor #EAF3FF",
        "skinparam NoteBorderColor #6C97C2",
        "skinparam Shadowing false",
        "skinparam ArrowColor #333333",
        "title %s" % _escape(title),
        "start",
    ]

    annotation_count = 0

    for step in display_steps:
        lines.append(
            ":%s;"
            % _escape(
                _step_label(
                    step,
                    counterexample,
                )
            )
        )

        note = annotations_by_step.get(step.step)

        if note and annotation_count < _MAX_ANNOTATIONS:
            cleaned_note = _clean_note(note)

            if cleaned_note:
                wrapped_lines = textwrap.wrap(cleaned_note, width=_MAX_NOTE_LENGTH)
                
                lines.append("note right")
                for w_line in wrapped_lines:
                    lines.append("  %s" % _escape(w_line))
                lines.append("end note")
                
                annotation_count += 1

    lines.append(
        ":VIOLATION\\n%s;"
        % _escape(
            _violation_label(
                counterexample
            )
        )
    )

    lines.append("stop")
    lines.append("@enduml")

    return "\n".join(lines)


def filter_valid_annotations(
    annotations: Iterable[StepAnnotation],
    counterexample: Counterexample,
) -> List[StepAnnotation]:
    """Drop annotations that do not reference a real trace step."""

    valid_steps = {
        step.step
        for step in counterexample.trace
    }

    return [
        annotation
        for annotation in annotations
        if annotation.step in valid_steps
    ]


def _select_display_steps(
    counterexample: Counterexample,
) -> List[TraceStep]:
    """Choose the most relevant student-facing trace states."""

    trace = list(counterexample.trace)

    if not trace:
        return []

    source_lines = _source_lines(
        counterexample.source_snippet
    )

    candidate_steps = [
        step
        for step in trace
        if _is_candidate_step(
            step,
            counterexample,
            source_lines,
        )
    ]

    candidate_steps = _deduplicate_steps(
        candidate_steps,
        counterexample,
    )

    candidate_steps = _compress_repeated_assignments(
        candidate_steps
    )

    if not candidate_steps:
        candidate_steps = [
            step
            for step in trace
            if not _is_internal_step(step)
        ]

        candidate_steps = _deduplicate_steps(
            candidate_steps,
            counterexample,
        )

        candidate_steps = _compress_repeated_assignments(
            candidate_steps
        )

    if not candidate_steps:
        return []

    if len(candidate_steps) <= _MAX_DISPLAY_STEPS:
        return candidate_steps

    important_names = _important_identifiers(
        counterexample
    )

    scored = [
        (
            _relevance_score(
                step,
                counterexample,
                source_lines,
                important_names,
            ),
            index,
            step,
        )
        for index, step in enumerate(candidate_steps)
    ]

    scored.sort(
        key=lambda item: (
            item[0],
            item[1],
        ),
        reverse=True,
    )

    selected = scored[:_MAX_DISPLAY_STEPS]
    selected_steps = {
        item[2].step
        for item in selected
    }

    # Restore execution order.
    return [
        step
        for step in candidate_steps
        if step.step in selected_steps
    ]


def _is_candidate_step(
    step: TraceStep,
    counterexample: Counterexample,
    source_lines: List[str],
) -> bool:
    """Return True when a step is suitable for the student-facing diagram."""

    if _is_internal_step(step):
        return False

    if step.file and counterexample.file:
        if not _same_file(
            step.file,
            counterexample.file,
        ):
            return False

    if (
        source_lines
        and step.line is not None
        and step.line > len(source_lines)
    ):
        return False

    event = (
        step.event or ""
    ).strip().lower()

    if (
        event == "program state reached"
        and step.line != counterexample.line
    ):
        return False

    return True


def _relevance_score(
    step: TraceStep,
    counterexample: Counterexample,
    source_lines: List[str],
    important_names: Set[str],
) -> int:
    """Score one trace step by how useful it is for explaining the bug."""

    score = 0

    if _same_file(
        step.file,
        counterexample.file,
    ):
        score += 8

    if (
        counterexample.function
        and step.function
        and step.function == counterexample.function
    ):
        score += 5

    if step.line is not None:
        score += 2

        if counterexample.line is not None:
            distance = abs(
                step.line
                - counterexample.line
            )

            if distance == 0:
                score += 12
            elif distance <= 2:
                score += 8
            elif distance <= 5:
                score += 4

    source_line = _source_line_text(
        source_lines,
        step.line,
    )

    combined = " ".join(
        [
            step.event or "",
            source_line,
            " ".join(
                variable.name
                for variable in step.variables
                if variable.name
            ),
        ]
    ).lower()

    for name in important_names:
        if name and name in combined:
            score += 6

    if step.variables:
        score += 3

    score += _violation_specific_score(
        step,
        counterexample,
        source_line,
    )

    return score


def _violation_specific_score(
    step: TraceStep,
    counterexample: Counterexample,
    source_line: str,
) -> int:
    """Add relevance based on the specific class of violation."""

    text = " ".join(
        [
            step.event or "",
            source_line,
        ]
    ).lower()

    if counterexample.violation_type == ViolationType.ARRAY_BOUNDS:
        if "[" in text and "]" in text:
            return 8
        if any(
            token in text
            for token in (
                "index",
                "array",
                "bounds",
            )
        ):
            return 4

    if counterexample.violation_type == ViolationType.NULL_SAFETY:
        if "->" in text or "*" in text:
            return 8
        if any(
            token in text
            for token in (
                "null",
                "nullptr",
                "pointer",
                "listener",
            )
        ):
            return 5

    if counterexample.violation_type == ViolationType.DIVISION_BY_ZERO:
        if "/" in text:
            return 8
        if any(
            token in text
            for token in (
                "zero",
                "divisor",
                "division",
            )
        ):
            return 5

    if counterexample.violation_type == ViolationType.LOOP_TERMINATION:
        if any(
            token in text
            for token in (
                "while",
                "for",
                "loop",
                "unwind",
            )
        ):
            return 8

    return 0


def _important_identifiers(
    counterexample: Counterexample,
) -> Set[str]:
    """Extract likely-important program identifiers from source and message."""

    pieces = [
        counterexample.message or "",
    ]

    source_line = _source_line_from_counterexample(
        counterexample
    )

    if source_line:
        pieces.append(
            source_line
        )

    text = " ".join(
        pieces
    )

    identifiers = set(
        re.findall(
            r"\b[A-Za-z_][A-Za-z0-9_]*\b",
            text,
        )
    )

    ignored = {
        "line",
        "array",
        "bounds",
        "violated",
        "failure",
        "dereference",
        "pointer",
        "null",
        "division",
        "zero",
        "program",
        "state",
        "reached",
        "int",
        "long",
        "signed",
        "unsigned",
        "void",
        "return",
        "if",
        "for",
        "while",
    }

    return {
        identifier.lower()
        for identifier in identifiers
        if identifier.lower() not in ignored
    }


def _compress_repeated_assignments(
    steps: List[TraceStep],
) -> List[TraceStep]:
    """Collapse consecutive updates of the same variable on the same line."""

    if not steps:
        return []

    result: List[TraceStep] = []
    pending: Optional[TraceStep] = None
    pending_variable: Optional[str] = None

    for step in steps:
        variable_names = [
            variable.name
            for variable in step.variables
            if variable.name
        ]

        current_variable = (
            variable_names[0]
            if len(variable_names) == 1
            else None
        )

        if (
            pending is not None
            and current_variable
            and current_variable == pending_variable
            and step.line == pending.line
        ):
            pending = step
            continue

        if pending is not None:
            result.append(
                pending
            )

        pending = step
        pending_variable = current_variable

    if pending is not None:
        result.append(
            pending
        )

    return result


def _deduplicate_steps(
    steps: List[TraceStep],
    counterexample: Counterexample,
) -> List[TraceStep]:
    """Remove duplicate student-facing states."""

    result: List[TraceStep] = []
    seen = set()

    for step in steps:
        signature = (
            step.line,
            step.function,
            _step_label(
                step,
                counterexample,
            ),
        )

        if signature in seen:
            continue

        seen.add(
            signature
        )

        result.append(
            step
        )

    return result


def _step_label(
    step: TraceStep,
    counterexample: Counterexample,
) -> str:
    """Create a concise source-aware label for one selected step."""

    source_lines = _source_lines(
        counterexample.source_snippet
    )

    source_text = _source_line_text(
        source_lines,
        step.line,
    )

    cleaned_source = _clean_source_line(
        source_text
    )

    # For the actual violation location, the student's source is usually
    # more informative than ESBMC's generic "Program state reached".
    if (
        step.line is not None
        and step.line == counterexample.line
        and cleaned_source
    ):
        return _truncate(
            "line %d: %s"
            % (
                step.line,
                cleaned_source,
            ),
            _MAX_LABEL_LENGTH,
        )

    if step.variables:
        assignments = ", ".join(
            "%s = %s"
            % (
                _clean_expression(
                    variable.name
                ),
                _clean_expression(
                    _truncate(
                        variable.value,
                        22,
                    )
                ),
            )
            for variable in step.variables
        )

        if step.line is not None:
            return _truncate(
                "line %d: %s"
                % (
                    step.line,
                    assignments,
                ),
                _MAX_LABEL_LENGTH,
            )

        return _truncate(
            assignments,
            _MAX_LABEL_LENGTH,
        )

    if cleaned_source:
        if step.line is not None:
            return _truncate(
                "line %d: %s"
                % (
                    step.line,
                    cleaned_source,
                ),
                _MAX_LABEL_LENGTH,
            )

        return _truncate(
            cleaned_source,
            _MAX_LABEL_LENGTH,
        )

    event = _clean_expression(
        step.event
    )

    if (
        event.strip().lower()
        == "program state reached"
    ):
        event = "violation reached"

    if step.line is not None:
        return _truncate(
            "line %d: %s"
            % (
                step.line,
                event,
            ),
            _MAX_LABEL_LENGTH,
        )

    return _truncate(
        event or "program state",
        _MAX_LABEL_LENGTH,
    )


def _violation_label(
    counterexample: Counterexample,
) -> str:
    """Return a short final violation label."""

    if counterexample.violation_type == ViolationType.ARRAY_BOUNDS:
        return "array index is outside the valid range"

    if counterexample.violation_type == ViolationType.NULL_SAFETY:
        return "null pointer dereference"

    if counterexample.violation_type == ViolationType.DIVISION_BY_ZERO:
        return "division by zero"

    if counterexample.violation_type == ViolationType.LOOP_TERMINATION:
        return "loop does not terminate correctly"

    return _truncate(
        _clean_expression(
            counterexample.message
        ),
        _MAX_LABEL_LENGTH,
    )


def _is_internal_step(
    step: TraceStep,
) -> bool:
    """Detect ESBMC/runtime/library trace noise."""

    text = " ".join(
        [
            step.event or "",
            step.function or "",
            step.file or "",
        ]
    ).lower()

    if "unknown location" in text:
        return True

    if any(
        token in text
        for token in _INTERNAL_TOKENS
    ):
        return True

    variable_names = {
        variable.name.strip().lower()
        for variable in step.variables
        if variable.name
    }

    if variable_names & _INTERNAL_VARIABLE_NAMES:
        return True

    return False


def _same_file(
    trace_file: str,
    submission_file: str,
) -> bool:
    """Check whether two trace/source paths refer to the same filename."""

    if not trace_file or not submission_file:
        return False

    trace_name = os.path.basename(
        trace_file.replace(
            "\\",
            "/",
        )
    )

    submission_name = os.path.basename(
        submission_file.replace(
            "\\",
            "/",
        )
    )

    return (
        trace_name.lower()
        == submission_name.lower()
    )


def _source_lines(
    source: str,
) -> List[str]:
    if not source:
        return []

    return source.splitlines()


def _source_line_text(
    source_lines: List[str],
    line_number: Optional[int],
) -> str:
    if (
        line_number is None
        or line_number < 1
        or line_number > len(source_lines)
    ):
        return ""

    return source_lines[
        line_number - 1
    ].strip()


def _source_line_from_counterexample(
    counterexample: Counterexample,
) -> str:
    return _source_line_text(
        _source_lines(
            counterexample.source_snippet
        ),
        counterexample.line,
    )


def _clean_source_line(
    text: str,
) -> str:
    """Simplify a C++ source line for display."""

    value = (
        text or ""
    ).strip()

    value = re.sub(
        r"//.*$",
        "",
        value,
    ).strip()

    value = value.rstrip(
        ";"
    ).strip()

    return _clean_expression(
        value
    )


def _clean_expression(
    text: str,
) -> str:
    """Remove checker-specific C/C++ noise while preserving meaning."""

    value = text or ""

    value = re.sub(
        r"\(\s*(?:signed|unsigned)?\s*"
        r"(?:long\s+long|long|short|int|char|bool|float|double)"
        r"(?:\s+int)?\s*\)",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = value.replace(
        "this->",
        "",
    )

    value = value.replace(
        "(*this).",
        "",
    )

    value = re.sub(
        r"__ESBMC_[A-Za-z0-9_]*",
        "",
        value,
    )

    value = re.sub(
        r"__CPROVER_[A-Za-z0-9_]*",
        "",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    ).strip()

    return value


def _clean_note(
    text: str,
) -> str:
    """Keep optional annotation text readable."""

    value = _clean_expression(
        text
    )

    replacements = (
        (
            "the program attempts to access the array at an invalid index",
            "Index is outside the valid array range",
        ),
        (
            "the program attempts to access memory at an invalid index",
            "Index is outside the valid range",
        ),
        (
            "the loop index has reached the size of the array",
            "Index reached the array boundary",
        ),
        (
            "the program attempts to use the null listener",
            "Pointer is null at this access",
        ),
    )

    lowered = value.lower()

    for old, new in replacements:
        if lowered.startswith(
            old
        ):
            return new

    return value


def _truncate(
    text: str,
    limit: int,
) -> str:
    text = text or ""

    if len(text) <= limit:
        return text

    return (
        text[: limit - 1].rstrip()
        + "\u2026"
    )


def _escape(
    text: str,
) -> str:
    """Escape text embedded in PlantUML."""

    return (
        (text or "")
        .replace("\\", "\\\\")
        .replace('"', "'")
        .replace(";", ",")
        .replace("\n", " ")
        .replace("\r", " ")
    )

# """Deterministic, source-aware PlantUML generation.

# The builder turns a verified counterexample into a small pedagogical
# execution diagram. It deliberately avoids rendering the raw checker trace
# verbatim. Instead it:

# - removes runtime/library noise;
# - prefers trace steps from the student's source file;
# - ranks steps by relevance to the violation;
# - collapses repeated loop/assignment states;
# - uses the student's actual source line where useful;
# - keeps the final diagram short and readable.

# The LLM never generates PlantUML syntax. Optional StepAnnotation values are
# plain-text notes only.
# """

# from __future__ import annotations

# import os
# import re
# from typing import Dict, Iterable, List, Optional, Set

# from .schemas import Counterexample, StepAnnotation, TraceStep, ViolationType


# _DIAGRAM_TITLES: Dict[ViolationType, str] = {
#     ViolationType.ARRAY_BOUNDS: "Execution Path - Array Bounds Violation",
#     ViolationType.NULL_SAFETY: "Execution Path - Null Pointer Dereference",
#     ViolationType.LOOP_TERMINATION: "Execution Path - Loop Termination",
#     ViolationType.DIVISION_BY_ZERO: "Execution Path - Division by Zero",
# }

# _MAX_DISPLAY_STEPS = 4
# _MAX_LABEL_LENGTH = 78
# _MAX_NOTE_LENGTH = 44
# _MAX_ANNOTATIONS = 1

# _INTERNAL_TOKENS = (
#     "stdin",
#     "stdout",
#     "stderr",
#     "virtual_table",
#     "std::",
#     "tag-std::",
#     "streambuf",
#     "seekoff",
#     "seekpos",
#     "showmanyc",
#     "underflow",
#     "overflow",
#     "__esbmc",
#     "__cprover",
#     "__gnu_cxx",
#     "__cxxabiv1",
#     "__static_initialization",
#     "__libc",
#     "_filesize",
# )

# _INTERNAL_VARIABLE_NAMES = {
#     "stdin",
#     "stdout",
#     "stderr",
#     "goodbit",
#     "badbit",
#     "failbit",
#     "eofbit",
#     "_filesize",
# }


# def build_execution_diagram(
#     counterexample: Counterexample,
#     annotations: Iterable[StepAnnotation] = (),
# ) -> str:
#     """Build a compact, source-aware PlantUML activity diagram."""

#     display_steps = _select_display_steps(counterexample)

#     annotations_by_step = {
#         annotation.step: annotation.note
#         for annotation in annotations
#     }

#     title = _DIAGRAM_TITLES.get(
#         counterexample.violation_type,
#         "Execution Path - Verification Failure",
#     )

#     lines: List[str] = [
#         "@startuml",
#         "skinparam defaultFontName Monospaced",
#         "skinparam ActivityBackgroundColor #FFFBE6",
#         "skinparam ActivityBorderColor #8A8A8A",
#         "skinparam NoteBackgroundColor #EAF3FF",
#         "skinparam NoteBorderColor #6C97C2",
#         "skinparam Shadowing false",
#         "skinparam ArrowColor #333333",
#         "title %s" % _escape(title),
#         "start",
#     ]

#     annotation_count = 0

#     for step in display_steps:
#         lines.append(
#             ":%s;"
#             % _escape(
#                 _step_label(
#                     step,
#                     counterexample,
#                 )
#             )
#         )

#         note = annotations_by_step.get(step.step)

#         if note and annotation_count < _MAX_ANNOTATIONS:
#             cleaned_note = _clean_note(note)

#             if cleaned_note:
#                 lines.append(
#                     "note right: %s"
#                     % _escape(
#                         _truncate(
#                             cleaned_note,
#                             _MAX_NOTE_LENGTH,
#                         )
#                     )
#                 )
#                 annotation_count += 1

#     lines.append(
#         ":VIOLATION\\n%s;"
#         % _escape(
#             _violation_label(
#                 counterexample
#             )
#         )
#     )

#     lines.append("stop")
#     lines.append("@enduml")

#     return "\n".join(lines)


# def filter_valid_annotations(
#     annotations: Iterable[StepAnnotation],
#     counterexample: Counterexample,
# ) -> List[StepAnnotation]:
#     """Drop annotations that do not reference a real trace step."""

#     valid_steps = {
#         step.step
#         for step in counterexample.trace
#     }

#     return [
#         annotation
#         for annotation in annotations
#         if annotation.step in valid_steps
#     ]


# def _select_display_steps(
#     counterexample: Counterexample,
# ) -> List[TraceStep]:
#     """Choose the most relevant student-facing trace states."""

#     trace = list(counterexample.trace)

#     if not trace:
#         return []

#     source_lines = _source_lines(
#         counterexample.source_snippet
#     )

#     candidate_steps = [
#         step
#         for step in trace
#         if _is_candidate_step(
#             step,
#             counterexample,
#             source_lines,
#         )
#     ]

#     candidate_steps = _deduplicate_steps(
#         candidate_steps,
#         counterexample,
#     )

#     candidate_steps = _compress_repeated_assignments(
#         candidate_steps
#     )

#     if not candidate_steps:
#         candidate_steps = [
#             step
#             for step in trace
#             if not _is_internal_step(step)
#         ]

#         candidate_steps = _deduplicate_steps(
#             candidate_steps,
#             counterexample,
#         )

#         candidate_steps = _compress_repeated_assignments(
#             candidate_steps
#         )

#     if not candidate_steps:
#         return []

#     if len(candidate_steps) <= _MAX_DISPLAY_STEPS:
#         return candidate_steps

#     important_names = _important_identifiers(
#         counterexample
#     )

#     scored = [
#         (
#             _relevance_score(
#                 step,
#                 counterexample,
#                 source_lines,
#                 important_names,
#             ),
#             index,
#             step,
#         )
#         for index, step in enumerate(candidate_steps)
#     ]

#     scored.sort(
#         key=lambda item: (
#             item[0],
#             item[1],
#         ),
#         reverse=True,
#     )

#     selected = scored[:_MAX_DISPLAY_STEPS]
#     selected_steps = {
#         item[2].step
#         for item in selected
#     }

#     # Restore execution order.
#     return [
#         step
#         for step in candidate_steps
#         if step.step in selected_steps
#     ]


# def _is_candidate_step(
#     step: TraceStep,
#     counterexample: Counterexample,
#     source_lines: List[str],
# ) -> bool:
#     """Return True when a step is suitable for the student-facing diagram."""

#     if _is_internal_step(step):
#         return False

#     if step.file and counterexample.file:
#         if not _same_file(
#             step.file,
#             counterexample.file,
#         ):
#             return False

#     if (
#         source_lines
#         and step.line is not None
#         and step.line > len(source_lines)
#     ):
#         return False

#     event = (
#         step.event or ""
#     ).strip().lower()

#     if (
#         event == "program state reached"
#         and step.line != counterexample.line
#     ):
#         return False

#     return True


# def _relevance_score(
#     step: TraceStep,
#     counterexample: Counterexample,
#     source_lines: List[str],
#     important_names: Set[str],
# ) -> int:
#     """Score one trace step by how useful it is for explaining the bug."""

#     score = 0

#     if _same_file(
#         step.file,
#         counterexample.file,
#     ):
#         score += 8

#     if (
#         counterexample.function
#         and step.function
#         and step.function == counterexample.function
#     ):
#         score += 5

#     if step.line is not None:
#         score += 2

#         if counterexample.line is not None:
#             distance = abs(
#                 step.line
#                 - counterexample.line
#             )

#             if distance == 0:
#                 score += 12
#             elif distance <= 2:
#                 score += 8
#             elif distance <= 5:
#                 score += 4

#     source_line = _source_line_text(
#         source_lines,
#         step.line,
#     )

#     combined = " ".join(
#         [
#             step.event or "",
#             source_line,
#             " ".join(
#                 variable.name
#                 for variable in step.variables
#                 if variable.name
#             ),
#         ]
#     ).lower()

#     for name in important_names:
#         if name and name in combined:
#             score += 6

#     if step.variables:
#         score += 3

#     score += _violation_specific_score(
#         step,
#         counterexample,
#         source_line,
#     )

#     return score


# def _violation_specific_score(
#     step: TraceStep,
#     counterexample: Counterexample,
#     source_line: str,
# ) -> int:
#     """Add relevance based on the specific class of violation."""

#     text = " ".join(
#         [
#             step.event or "",
#             source_line,
#         ]
#     ).lower()

#     if counterexample.violation_type == ViolationType.ARRAY_BOUNDS:
#         if "[" in text and "]" in text:
#             return 8
#         if any(
#             token in text
#             for token in (
#                 "index",
#                 "array",
#                 "bounds",
#             )
#         ):
#             return 4

#     if counterexample.violation_type == ViolationType.NULL_SAFETY:
#         if "->" in text or "*" in text:
#             return 8
#         if any(
#             token in text
#             for token in (
#                 "null",
#                 "nullptr",
#                 "pointer",
#                 "listener",
#             )
#         ):
#             return 5

#     if counterexample.violation_type == ViolationType.DIVISION_BY_ZERO:
#         if "/" in text:
#             return 8
#         if any(
#             token in text
#             for token in (
#                 "zero",
#                 "divisor",
#                 "division",
#             )
#         ):
#             return 5

#     if counterexample.violation_type == ViolationType.LOOP_TERMINATION:
#         if any(
#             token in text
#             for token in (
#                 "while",
#                 "for",
#                 "loop",
#                 "unwind",
#             )
#         ):
#             return 8

#     return 0


# def _important_identifiers(
#     counterexample: Counterexample,
# ) -> Set[str]:
#     """Extract likely-important program identifiers from source and message."""

#     pieces = [
#         counterexample.message or "",
#     ]

#     source_line = _source_line_from_counterexample(
#         counterexample
#     )

#     if source_line:
#         pieces.append(
#             source_line
#         )

#     text = " ".join(
#         pieces
#     )

#     identifiers = set(
#         re.findall(
#             r"\b[A-Za-z_][A-Za-z0-9_]*\b",
#             text,
#         )
#     )

#     ignored = {
#         "line",
#         "array",
#         "bounds",
#         "violated",
#         "failure",
#         "dereference",
#         "pointer",
#         "null",
#         "division",
#         "zero",
#         "program",
#         "state",
#         "reached",
#         "int",
#         "long",
#         "signed",
#         "unsigned",
#         "void",
#         "return",
#         "if",
#         "for",
#         "while",
#     }

#     return {
#         identifier.lower()
#         for identifier in identifiers
#         if identifier.lower() not in ignored
#     }


# def _compress_repeated_assignments(
#     steps: List[TraceStep],
# ) -> List[TraceStep]:
#     """Collapse consecutive updates of the same variable on the same line."""

#     if not steps:
#         return []

#     result: List[TraceStep] = []
#     pending: Optional[TraceStep] = None
#     pending_variable: Optional[str] = None

#     for step in steps:
#         variable_names = [
#             variable.name
#             for variable in step.variables
#             if variable.name
#         ]

#         current_variable = (
#             variable_names[0]
#             if len(variable_names) == 1
#             else None
#         )

#         if (
#             pending is not None
#             and current_variable
#             and current_variable == pending_variable
#             and step.line == pending.line
#         ):
#             pending = step
#             continue

#         if pending is not None:
#             result.append(
#                 pending
#             )

#         pending = step
#         pending_variable = current_variable

#     if pending is not None:
#         result.append(
#             pending
#         )

#     return result


# def _deduplicate_steps(
#     steps: List[TraceStep],
#     counterexample: Counterexample,
# ) -> List[TraceStep]:
#     """Remove duplicate student-facing states."""

#     result: List[TraceStep] = []
#     seen = set()

#     for step in steps:
#         signature = (
#             step.line,
#             step.function,
#             _step_label(
#                 step,
#                 counterexample,
#             ),
#         )

#         if signature in seen:
#             continue

#         seen.add(
#             signature
#         )

#         result.append(
#             step
#         )

#     return result


# def _step_label(
#     step: TraceStep,
#     counterexample: Counterexample,
# ) -> str:
#     """Create a concise source-aware label for one selected step."""

#     source_lines = _source_lines(
#         counterexample.source_snippet
#     )

#     source_text = _source_line_text(
#         source_lines,
#         step.line,
#     )

#     cleaned_source = _clean_source_line(
#         source_text
#     )

#     # For the actual violation location, the student's source is usually
#     # more informative than ESBMC's generic "Program state reached".
#     if (
#         step.line is not None
#         and step.line == counterexample.line
#         and cleaned_source
#     ):
#         return _truncate(
#             "line %d: %s"
#             % (
#                 step.line,
#                 cleaned_source,
#             ),
#             _MAX_LABEL_LENGTH,
#         )

#     if step.variables:
#         assignments = ", ".join(
#             "%s = %s"
#             % (
#                 _clean_expression(
#                     variable.name
#                 ),
#                 _clean_expression(
#                     _truncate(
#                         variable.value,
#                         22,
#                     )
#                 ),
#             )
#             for variable in step.variables
#         )

#         if step.line is not None:
#             return _truncate(
#                 "line %d: %s"
#                 % (
#                     step.line,
#                     assignments,
#                 ),
#                 _MAX_LABEL_LENGTH,
#             )

#         return _truncate(
#             assignments,
#             _MAX_LABEL_LENGTH,
#         )

#     if cleaned_source:
#         if step.line is not None:
#             return _truncate(
#                 "line %d: %s"
#                 % (
#                     step.line,
#                     cleaned_source,
#                 ),
#                 _MAX_LABEL_LENGTH,
#             )

#         return _truncate(
#             cleaned_source,
#             _MAX_LABEL_LENGTH,
#         )

#     event = _clean_expression(
#         step.event
#     )

#     if (
#         event.strip().lower()
#         == "program state reached"
#     ):
#         event = "violation reached"

#     if step.line is not None:
#         return _truncate(
#             "line %d: %s"
#             % (
#                 step.line,
#                 event,
#             ),
#             _MAX_LABEL_LENGTH,
#         )

#     return _truncate(
#         event or "program state",
#         _MAX_LABEL_LENGTH,
#     )


# def _violation_label(
#     counterexample: Counterexample,
# ) -> str:
#     """Return a short final violation label."""

#     if counterexample.violation_type == ViolationType.ARRAY_BOUNDS:
#         return "array index is outside the valid range"

#     if counterexample.violation_type == ViolationType.NULL_SAFETY:
#         return "null pointer dereference"

#     if counterexample.violation_type == ViolationType.DIVISION_BY_ZERO:
#         return "division by zero"

#     if counterexample.violation_type == ViolationType.LOOP_TERMINATION:
#         return "loop does not terminate correctly"

#     return _truncate(
#         _clean_expression(
#             counterexample.message
#         ),
#         _MAX_LABEL_LENGTH,
#     )


# def _is_internal_step(
#     step: TraceStep,
# ) -> bool:
#     """Detect ESBMC/runtime/library trace noise."""

#     text = " ".join(
#         [
#             step.event or "",
#             step.function or "",
#             step.file or "",
#         ]
#     ).lower()

#     if "unknown location" in text:
#         return True

#     if any(
#         token in text
#         for token in _INTERNAL_TOKENS
#     ):
#         return True

#     variable_names = {
#         variable.name.strip().lower()
#         for variable in step.variables
#         if variable.name
#     }

#     if variable_names & _INTERNAL_VARIABLE_NAMES:
#         return True

#     return False


# def _same_file(
#     trace_file: str,
#     submission_file: str,
# ) -> bool:
#     """Check whether two trace/source paths refer to the same filename."""

#     if not trace_file or not submission_file:
#         return False

#     trace_name = os.path.basename(
#         trace_file.replace(
#             "\\",
#             "/",
#         )
#     )

#     submission_name = os.path.basename(
#         submission_file.replace(
#             "\\",
#             "/",
#         )
#     )

#     return (
#         trace_name.lower()
#         == submission_name.lower()
#     )


# def _source_lines(
#     source: str,
# ) -> List[str]:
#     if not source:
#         return []

#     return source.splitlines()


# def _source_line_text(
#     source_lines: List[str],
#     line_number: Optional[int],
# ) -> str:
#     if (
#         line_number is None
#         or line_number < 1
#         or line_number > len(source_lines)
#     ):
#         return ""

#     return source_lines[
#         line_number - 1
#     ].strip()


# def _source_line_from_counterexample(
#     counterexample: Counterexample,
# ) -> str:
#     return _source_line_text(
#         _source_lines(
#             counterexample.source_snippet
#         ),
#         counterexample.line,
#     )


# def _clean_source_line(
#     text: str,
# ) -> str:
#     """Simplify a C++ source line for display."""

#     value = (
#         text or ""
#     ).strip()

#     value = re.sub(
#         r"//.*$",
#         "",
#         value,
#     ).strip()

#     value = value.rstrip(
#         ";"
#     ).strip()

#     return _clean_expression(
#         value
#     )


# def _clean_expression(
#     text: str,
# ) -> str:
#     """Remove checker-specific C/C++ noise while preserving meaning."""

#     value = text or ""

#     value = re.sub(
#         r"\(\s*(?:signed|unsigned)?\s*"
#         r"(?:long\s+long|long|short|int|char|bool|float|double)"
#         r"(?:\s+int)?\s*\)",
#         "",
#         value,
#         flags=re.IGNORECASE,
#     )

#     value = value.replace(
#         "this->",
#         "",
#     )

#     value = value.replace(
#         "(*this).",
#         "",
#     )

#     value = re.sub(
#         r"__ESBMC_[A-Za-z0-9_]*",
#         "",
#         value,
#     )

#     value = re.sub(
#         r"__CPROVER_[A-Za-z0-9_]*",
#         "",
#         value,
#     )

#     value = re.sub(
#         r"\s+",
#         " ",
#         value,
#     ).strip()

#     return value


# def _clean_note(
#     text: str,
# ) -> str:
#     """Keep optional annotation text compact."""

#     value = _clean_expression(
#         text
#     )

#     replacements = (
#         (
#             "the program attempts to access the array at an invalid index",
#             "Index is outside the valid array range",
#         ),
#         (
#             "the program attempts to access memory at an invalid index",
#             "Index is outside the valid range",
#         ),
#         (
#             "the loop index has reached the size of the array",
#             "Index reached the array boundary",
#         ),
#         (
#             "the program attempts to use the null listener",
#             "Pointer is null at this access",
#         ),
#     )

#     lowered = value.lower()

#     for old, new in replacements:
#         if lowered.startswith(
#             old
#         ):
#             return new

#     return _truncate(
#         value,
#         _MAX_NOTE_LENGTH,
#     )


# def _truncate(
#     text: str,
#     limit: int,
# ) -> str:
#     text = text or ""

#     if len(text) <= limit:
#         return text

#     return (
#         text[: limit - 1].rstrip()
#         + "\u2026"
#     )


# def _escape(
#     text: str,
# ) -> str:
#     """Escape text embedded in PlantUML."""

#     return (
#         (text or "")
#         .replace("\\", "\\\\")
#         .replace('"', "'")
#         .replace(";", ",")
#         .replace("\n", " ")
#         .replace("\r", " ")
#     )
