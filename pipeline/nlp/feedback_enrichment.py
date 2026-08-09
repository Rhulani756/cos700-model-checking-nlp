"""Attaches a diagram to an already-generated FeedbackGenerationResult.

This is deliberately a separate step from LLM generation, not folded into
LLMClient.generate_feedback_sync/async. If the diagram render fails (the
PlantUML server is down, a network hiccup, etc.) it must never take down
the primary text feedback response - the textual feedback is already
complete and valid at this point.

Call this right after you get a FeedbackGenerationResult back from
LLMClient, before returning the result to the API layer:

    result = client.generate_feedback_sync(parser_output)
    result = enrich_with_diagram_sync(result, counterexample)
"""

from __future__ import annotations

import logging

from .diagram_builder import build_execution_diagram, filter_valid_annotations
from .exceptions import DiagramRenderError
from .plantuml_renderer import render_svg_async, render_svg_sync
from .schemas import Counterexample, FeedbackGenerationResult

logger = logging.getLogger(__name__)


def enrich_with_diagram_sync(
    result: FeedbackGenerationResult,
    counterexample: Counterexample,
) -> FeedbackGenerationResult:
    """Build and render the execution-path diagram, attaching it to result.

    Never raises. On any failure, diagram_plantuml/diagram_svg stay empty
    and diagram_render_error carries a short reason, so the caller can
    decide whether to show a "diagram unavailable" note without losing
    the text feedback.
    """

    valid_annotations = filter_valid_annotations(
        result.feedback.step_annotations, counterexample
    )
    plantuml_source = build_execution_diagram(counterexample, valid_annotations)
    result.diagram_plantuml = plantuml_source

    try:
        result.diagram_svg = render_svg_sync(plantuml_source)
    except DiagramRenderError as error:
        logger.warning("Diagram render failed, continuing without SVG: %s", error)
        result.diagram_render_error = str(error)

    return result


async def enrich_with_diagram_async(
    result: FeedbackGenerationResult,
    counterexample: Counterexample,
) -> FeedbackGenerationResult:
    """Async counterpart to enrich_with_diagram_sync, for FastAPI routes."""

    valid_annotations = filter_valid_annotations(
        result.feedback.step_annotations, counterexample
    )
    plantuml_source = build_execution_diagram(counterexample, valid_annotations)
    result.diagram_plantuml = plantuml_source

    try:
        result.diagram_svg = await render_svg_async(plantuml_source)
    except DiagramRenderError as error:
        logger.warning("Diagram render failed, continuing without SVG: %s", error)
        result.diagram_render_error = str(error)

    return result
