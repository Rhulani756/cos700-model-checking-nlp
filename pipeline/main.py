# Entry point for the end-to-end pipeline
# Student Input → Model Checker → Parser → NLP Module → Feedback Output

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Literal

from pipeline.model_checker.esbmc_runner import ESBMCRunner
from pipeline.parser.counterexample_parser import parse
from pipeline.nlp.llm_client import LLMClient
from pipeline.nlp.schemas import Counterexample
from pipeline.snippet import extract_snippet

logger = logging.getLogger(__name__)

CompilationMode = Literal["independent", "combined"]


def discover_source_files(submission_dir: Path) -> List[Path]:
    return sorted(submission_dir.rglob("*.cpp"))


async def _generate_feedback_for_entry(
    entry: Dict[str, Any],
    parsed: Dict[str, Any],
    src_file: Path,
    llm_client: LLMClient,
) -> None:
    parsed.setdefault("tool", "esbmc")

    try:
        parsed["source_snippet"] = extract_snippet(src_file, parsed.get("line"))
    except Exception:
        logger.warning("Snippet extraction failed for %s; falling back to full file.", src_file)
        try:
            parsed["source_snippet"] = src_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            parsed["source_snippet"] = ""

    try:
        counterexample = Counterexample.model_validate(parsed)
        generation_result = await llm_client.generate_feedback(counterexample)

        entry["feedback"] = generation_result.feedback.model_dump()
        entry["feedback_meta"] = {
            "provider": generation_result.provider,
            "model": generation_result.model,
            "prompt_version": generation_result.prompt_version,
            "used_fallback": generation_result.used_fallback,
            "latency_ms": generation_result.latency_ms,
        }
        entry["counterexample"] = counterexample.model_dump()
        entry["diagram"] = {
            "plantuml": generation_result.diagram_plantuml,
            "svg": generation_result.diagram_svg,
            "render_error": generation_result.diagram_render_error,
        }
    except Exception as exc:
        logger.error("Feedback generation failed for %s: %s", src_file, exc)
        entry["feedback_error"] = str(exc)


async def _run_independent(
    submission_dir: Path,
    source_files: List[Path],
    checker: ESBMCRunner,
    llm_client: LLMClient,
) -> List[Dict[str, Any]]:
    """independent exercise"""
    results: List[Dict[str, Any]] = []

    for src_file in source_files:
        logger.debug("Running model checker on: %s", src_file)
        raw_output = await asyncio.to_thread(checker.run, src_file)
        parsed = parse(raw_output)
        verification_result = parsed.get("verification_result", "ERROR")

        entry: Dict[str, Any] = {
            "file": str(src_file.relative_to(submission_dir)),
            "verification_result": verification_result,
            "raw_output": raw_output,
            "feedback": None,
        }

        if verification_result == "FAILED":
            await _generate_feedback_for_entry(entry, parsed, src_file, llm_client)
        else:
            logger.info("No violation detected in %s; skipping feedback generation.", src_file)

        results.append(entry)

    return results


async def _run_combined(
    submission_dir: Path,
    source_files: List[Path],
    checker: ESBMCRunner,
    llm_client: LLMClient,
) -> List[Dict[str, Any]]:
    """All .cpp files together - one program"""
    logger.debug("Running model checker on combined submission: %s", source_files)
    raw_output = await asyncio.to_thread(checker.run, source_files)
    parsed = parse(raw_output)
    verification_result = parsed.get("verification_result", "ERROR")

    violation_file = parsed.get("file", "")
    try:
        relative_violation_file = str(Path(violation_file).resolve().relative_to(submission_dir))
    except (ValueError, OSError):
        relative_violation_file = violation_file or "combined submission"

    entry: Dict[str, Any] = {
        "file": relative_violation_file,
        "all_files": [str(f.relative_to(submission_dir)) for f in source_files],
        "verification_result": verification_result,
        "raw_output": raw_output,
        "feedback": None,
    }

    if verification_result == "FAILED":
        try:
            target_file = Path(violation_file).resolve()
            if not target_file.is_file():
                raise FileNotFoundError
        except (FileNotFoundError, OSError):
            target_file = source_files[0]
            logger.warning(
                "Could not resolve violation file '%s'; falling back to %s for snippet.",
                violation_file, target_file,
            )

        await _generate_feedback_for_entry(entry, parsed, target_file, llm_client)
    else:
        logger.info("No violation detected across combined submission.")

    return [entry]


async def run_pipeline(
    submission_dir: Path,
    mode: CompilationMode = "independent",
) -> Dict[str, Any]:
    submission_dir = Path(submission_dir).resolve()
    if not submission_dir.is_dir():
        raise FileNotFoundError(f"Submission directory not found: {submission_dir}")

    source_files = discover_source_files(submission_dir)
    if not source_files:
        raise ValueError(f"No .cpp files found in {submission_dir}")

    checker = ESBMCRunner()
    llm_client = LLMClient.from_env()

    if mode == "combined":
        results = await _run_combined(submission_dir, source_files, checker, llm_client)
    else:
        results = await _run_independent(submission_dir, source_files, checker, llm_client)

    return {"submission_dir": str(submission_dir), "mode": mode, "results": results}


# ======================================================================================================

# import asyncio
# import logging
# from pathlib import Path
# from typing import Any, Dict, List

# from pipeline.model_checker.esbmc_runner import ESBMCRunner
# from pipeline.parser.counterexample_parser import parse
# from pipeline.nlp.llm_client import LLMClient
# from pipeline.nlp.schemas import Counterexample
# from pipeline.snippet import extract_snippet  # ASSUMPTION: signature (path, line) -> str

# logger = logging.getLogger(__name__)


# def discover_source_files(submission_dir: Path) -> List[Path]:
#     return sorted(submission_dir.rglob("*.cpp"))


# async def run_pipeline(submission_dir: Path) -> Dict[str, Any]:
#     submission_dir = Path(submission_dir).resolve()
#     if not submission_dir.is_dir():
#         raise FileNotFoundError(f"Submission directory not found: {submission_dir}")

#     source_files = discover_source_files(submission_dir)
#     if not source_files:
#         raise ValueError(f"No .cpp files found in {submission_dir}")

#     checker = ESBMCRunner()
#     llm_client = LLMClient.from_env()

#     results: List[Dict[str, Any]] = []

#     for src_file in source_files:
#         logger.debug("Running model checker on: %s", src_file)

#         # ESBMCRunner.run() blocks on subprocess.run — offload it so it
#         # doesn't stall the event loop while other requests are being served.
#         raw_output = await asyncio.to_thread(checker.run, src_file)
#         logger.debug("Raw model checker output for %s:\n%s", src_file, raw_output)

#         parsed = parse(raw_output)
#         logger.debug("Parsed output for %s:\n%s", src_file, parsed)

#         verification_result = parsed.get("verification_result", "ERROR")

#         entry: Dict[str, Any] = {
#             "file": str(src_file.relative_to(submission_dir)),
#             "verification_result": verification_result,
#             "raw_output": raw_output,
#             "feedback": None,
#         }

#         if verification_result == "FAILED":
#             parsed.setdefault("tool", "esbmc")

#             try:
#                 parsed["source_snippet"] = extract_snippet(src_file, parsed.get("line"))
#             except Exception:
#                 logger.warning("Snippet extraction failed for %s; falling back to full file.", src_file)
#                 try:
#                     parsed["source_snippet"] = src_file.read_text(encoding="utf-8", errors="replace")
#                 except OSError:
#                     parsed["source_snippet"] = ""

#             counterexample = Counterexample.model_validate(parsed)
#             generation_result = await llm_client.generate_feedback(counterexample)

#             entry["feedback"] = generation_result.feedback.model_dump()
#             entry["feedback_meta"] = {
#                 "provider": generation_result.provider,
#                 "model": generation_result.model,
#                 "prompt_version": generation_result.prompt_version,
#                 "used_fallback": generation_result.used_fallback,
#                 "latency_ms": generation_result.latency_ms,
#             }
#             entry["counterexample"] = counterexample.model_dump()
#             entry["diagram"] = {
#                 "plantuml": generation_result.diagram_plantuml,
#                 "svg": generation_result.diagram_svg,
#                 "render_error": generation_result.diagram_render_error,
#             }
#         else:
#             logger.info("No violation detected in %s; skipping feedback generation.", src_file)

#         results.append(entry)

#     return {"submission_dir": str(submission_dir), "results": results}


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

#     PIPELINE_DIR = Path(__file__).resolve().parent
#     PROGRAMS_DIR = PIPELINE_DIR.parent / "data" / "programs"

#     asyncio.run(run_pipeline(PROGRAMS_DIR / "array_bounds"))

# ===================================================================================================================

# # Entry point for the end-to-end pipeline
# # Student Input → Model Checker → Parser → NLP Module → Feedback Output

# import logging
# from pathlib import Path
# from typing import Any, Dict, Union

# from model_checker.esbmc_runner import ESBMCRunner
# from parser.counterexample_parser import parse
# from snippet import extract_snippet

# logger = logging.getLogger(__name__)

# PIPELINE_DIR = Path(__file__).resolve().parent
# PROGRAMS_DIR = PIPELINE_DIR.parent / "data" / "programs"

# runner = ESBMCRunner()


# def run_pipeline(submission_path: Union[str, Path]) -> Dict[str, Any]:
#     """
#     Executes the model checking pipeline.

#     Args:
#         submission_path: Path to the student's C++ submission.

#     Returns:
#         <tbd>
#     """
#     logger.debug("Running model checker on: %s", submission_path)
#     raw_output = runner.run(submission_path)
#     logger.debug("Raw model checker output:\n%s", raw_output)

#     parsed_output = parse(raw_output)
#     logger.debug("Parsed output:\n%s", parsed_output)

#     if parsed_output.get("verification_result") != "FAILED":
#         logger.info("No violation detected; skipping feedback generation.")
#         return parsed_output

#     snippet = extract_snippet(submission_path, parsed_output["line"])
#     logger.debug("Extracted snippet (lines 1-%d):\n%s", parsed_output["line"], snippet)

#     # result = client.generate_feedback_sync(parsed_output, snippet)

#     return parsed_output # TODO change to "result" later


# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s") # change INFO to DEBUG to see raw esbmc output and parsed output
#     run_pipeline(PROGRAMS_DIR / "array_bounds" / "array_bounds_01_student_grades.cpp")
#     # run_pipeline(PROGRAMS_DIR / "div_zero" / "<file_name_here>.cpp")
#     # run_pipeline(PROGRAMS_DIR / "infinite_loop" / "<file_name_here>.cpp")
#     # run_pipeline(PROGRAMS_DIR / "null_pointer" / "<file_name_here>.cpp")