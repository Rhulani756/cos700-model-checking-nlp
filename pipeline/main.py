# pipeline/main.py
import asyncio
import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from pipeline.model_checker.esbmc_runner import ESBMCRunner
from pipeline.parser.counterexample_parser import ESBMCParser
from pipeline.snippet import extract_snippet
from pipeline.nlp.llm_client import LLMClient


logger = logging.getLogger(__name__)

runner = ESBMCRunner()
parser = ESBMCParser()

OnStage = Callable[[str, str], None]


def _emit(on_stage: Optional[OnStage], stage: str, detail: str = "") -> None:
    if on_stage:
        on_stage(stage, detail)


async def run_pipeline(
    submission_path: Union[str, Path],
    mode: str = "single",
    on_stage: Optional[OnStage] = None,
) -> Dict[str, Any]:
    submission_dir = Path(submission_path).resolve()

    if not submission_dir.exists():
        raise FileNotFoundError("Submission path not found: %s" % submission_dir)
    if not submission_dir.is_dir():
        raise ValueError("Expected a submission directory, received: %s" % submission_dir)

    _emit(on_stage, "discovering_files")
    source_files = _find_source_files(submission_dir)

    if not source_files:
        raise ValueError("No C++ source files were found in submission: %s" % submission_dir)

    logger.info("Running pipeline for %d source file(s). Mode: %s", len(source_files), mode)

    if _is_combined_mode(mode):
        results = await _run_combined(source_files, on_stage=on_stage)
    else:
        results = []
        for source_file in source_files:
            result = await _run_single_file(source_file, on_stage=on_stage)
            results.append(result)

    _emit(on_stage, "done")
    return {"results": results}


async def _run_single_file(
    source_file: Path,
    on_stage: Optional[OnStage] = None,
) -> Dict[str, Any]:
    logger.debug("Running model checker on: %s", source_file)
    _emit(on_stage, "running_model_checker", source_file.name)

    raw_output, raw_multi_output = await asyncio.to_thread(runner.run, source_file)
    _raise_if_checker_error(raw_output, source_file)

    logger.debug("Raw singular-trace output for %s:\n%s", source_file.name, raw_output)
    logger.debug("Raw multi-property output for %s:\n%s", source_file.name, raw_multi_output)

    _emit(on_stage, "parsing_output", source_file.name)
    singular, multi = parser.parse(raw_output, raw_multi_output)

    logger.debug("Parsed singular output for %s:\n%s", source_file.name, singular)
    logger.debug("Parsed multi output for %s:\n%s", source_file.name, multi)

    return await _build_result(
        source_file=source_file,
        raw_output=raw_output,
        singular=singular,
        multi=multi,
        on_stage=on_stage,
    )


async def _run_combined(
    source_files: List[Path],
    on_stage: Optional[OnStage] = None,
) -> List[Dict[str, Any]]:
    logger.debug("Running model checker on combined submission: %s", source_files)
    _emit(on_stage, "running_model_checker", "combined submission")

    raw_output, raw_multi_output = await asyncio.to_thread(runner.run, source_files)
    _raise_if_checker_error(raw_output, source_files[0])

    logger.debug("Raw combined singular output:\n%s", raw_output)
    logger.debug("Raw combined multi output:\n%s", raw_multi_output)

    _emit(on_stage, "parsing_output", "combined submission")
    singular, multi = parser.parse(raw_output, raw_multi_output)

    logger.debug("Parsed combined singular output:\n%s", singular)
    logger.debug("Parsed combined multi output:\n%s", multi)

    verification_result = singular.get("verification_result")
    if not verification_result:
        raise ValueError("Parser did not return a verification_result for the combined submission.")

    if verification_result == "FAILED":
        source_file = _find_counterexample_file(singular, source_files)
    else:
        source_file = source_files[0]

    result = await _build_result(
        source_file=source_file,
        raw_output=raw_output,
        singular=singular,
        multi=multi,
        on_stage=on_stage,
    )

    return [result]


async def _build_result(
    source_file: Path,
    raw_output: str,
    singular: Dict[str, Any],
    multi: Dict[str, Any],
    on_stage: Optional[OnStage] = None,
) -> Dict[str, Any]:
    verification_result = singular.get("verification_result")
    if not verification_result:
        raise ValueError(
            "Parser did not return verification_result for file '%s'. Parsed output: %r"
            % (source_file.name, singular)
        )

    entry: Dict[str, Any] = {
        "file": source_file.name,
        "verification_result": verification_result,
        "raw_output": raw_output,
        "counterexample": None,
        "feedback": None,
        "diagram": {"plantuml": "", "svg": "", "render_error": ""},
        "passed_properties": multi.get("passed", []),
        "failed_properties": multi.get("failed", []),
        "undetermined_properties": multi.get("undetermined", []),
    }

    if verification_result != "FAILED":
        logger.info("No violation detected in %s; skipping feedback generation.", source_file.name)
        return entry

    counterexample = dict(singular)
    failing_line = counterexample.get("line")

    if failing_line:
        source = extract_snippet(source_file, failing_line)
        logger.debug(
            "Extracted snippet for %s (lines 1-%s):\n%s", source_file.name, failing_line, source
        )
    else:
        source = source_file.read_text(encoding="utf-8")
        logger.debug("No failing line for %s; supplying complete source.", source_file.name)

    counterexample["source_snippet"] = source
    entry["counterexample"] = counterexample

    logger.debug("NLP input for %s:\n%s", source_file.name, counterexample)

    try:
        _emit(on_stage, "generating_feedback", source_file.name)

        client = LLMClient.from_env()
        generation_result = await client.generate_feedback(counterexample)

        entry["feedback"] = generation_result.feedback.model_dump()

        _emit(on_stage, "rendering_diagram", source_file.name)

        entry["diagram"] = {
            "plantuml": generation_result.diagram_plantuml,
            "svg": generation_result.diagram_svg,
            "render_error": generation_result.diagram_render_error,
        }

        logger.info("Feedback generated successfully for %s.", source_file.name)

    except Exception as error:
        logger.exception("Feedback generation failed for %s.", source_file.name)
        entry["feedback_error"] = str(error)

    return entry


def _find_source_files(submission_dir: Path) -> List[Path]:
    supported_extensions = {".cpp", ".cc", ".cxx", ".c++"}
    files = [
        path for path in submission_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in supported_extensions
    ]
    return sorted(files, key=lambda path: str(path).lower())


def _find_counterexample_file(singular: Dict[str, Any], source_files: List[Path]) -> Path:
    parser_file = str(singular.get("file", "") or "")
    if parser_file:
        parser_name = Path(parser_file.replace("\\", "/")).name.lower()
        for source_file in source_files:
            if source_file.name.lower() == parser_name:
                return source_file
    return source_files[0]


def _is_combined_mode(mode: str) -> bool:
    normalized = str(mode or "").strip().lower().replace("-", "_").replace(" ", "_")
    return normalized in {
        "combined", "combine", "project", "whole_project",
        "multi_file", "multifile", "together", "all",
    }


def _raise_if_checker_error(raw_output: str, source_file: Path) -> None:
    stripped = (raw_output or "").strip()
    if not stripped:
        raise RuntimeError("ESBMC returned no output for %s." % source_file.name)
    if stripped.startswith("Error:"):
        raise RuntimeError(stripped)