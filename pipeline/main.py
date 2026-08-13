# Entry point for the end-to-end pipeline
# Student Input → Model Checker → Parser → NLP Module → Feedback Output

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pipeline.model_checker.esbmc_runner import ESBMCRunner
from pipeline.parser.counterexample_parser import parse
from pipeline.snippet import extract_snippet
from pipeline.nlp.llm_client import LLMClient


logger = logging.getLogger(__name__)

runner = ESBMCRunner()


async def run_pipeline(
    submission_path: Union[str, Path],
    mode: str = "single",
) -> Dict[str, Any]:
    """
    Run the complete pipeline for an uploaded submission directory.

    Flow:
        Uploaded C++ source
        → ESBMC
        → Parser
        → NLP feedback
        → Diagram
        → Backend-ready result

    Args:
        submission_path:
            Directory containing the uploaded C++ submission.

        mode:
            Compilation mode supplied by the backend.

    Returns:
        {
            "results": [
                {
                    "file": "...",
                    "verification_result": "...",
                    "raw_output": "...",
                    "counterexample": {...} | None,
                    "feedback": {...} | None,
                    "diagram": {
                        "plantuml": "...",
                        "svg": "...",
                        "render_error": "..."
                    }
                }
            ]
        }
    """

    submission_dir = Path(submission_path).resolve()

    if not submission_dir.exists():
        raise FileNotFoundError(
            "Submission path not found: %s"
            % submission_dir
        )

    if not submission_dir.is_dir():
        raise ValueError(
            "Expected a submission directory, received: %s"
            % submission_dir
        )

    source_files = _find_source_files(
        submission_dir
    )

    if not source_files:
        raise ValueError(
            "No C++ source files were found in submission: %s"
            % submission_dir
        )

    logger.info(
        "Running pipeline for %d source file(s). Mode: %s",
        len(source_files),
        mode,
    )

    if _is_combined_mode(mode):
        results = await _run_combined(
            source_files
        )
    else:
        results = []

        for source_file in source_files:
            result = await _run_single_file(
                source_file
            )

            results.append(result)

    return {
        "results": results,
    }


async def _run_single_file(
    source_file: Path,
) -> Dict[str, Any]:
    """Run the complete pipeline for one uploaded C++ source file."""

    logger.debug(
        "Running model checker on: %s",
        source_file,
    )

    # ESBMC is synchronous, so run it outside the async event loop.
    raw_output = await asyncio.to_thread(
        runner.run,
        source_file,
    )

    _raise_if_checker_error(
        raw_output,
        source_file,
    )

    logger.debug(
        "Raw model checker output for %s:\n%s",
        source_file.name,
        raw_output,
    )

    parsed_output = parse(
        raw_output
    )

    logger.debug(
        "Parsed output for %s:\n%s",
        source_file.name,
        parsed_output,
    )

    return await _build_result(
        source_file=source_file,
        raw_output=raw_output,
        parsed_output=parsed_output,
    )


async def _run_combined(
    source_files: List[Path],
) -> List[Dict[str, Any]]:
    """Run ESBMC once using all uploaded C++ files together."""

    logger.debug(
        "Running model checker on combined submission: %s",
        source_files,
    )

    raw_output = await asyncio.to_thread(
        runner.run,
        source_files,
    )

    _raise_if_checker_error(
        raw_output,
        source_files[0],
    )

    logger.debug(
        "Raw combined model checker output:\n%s",
        raw_output,
    )

    parsed_output = parse(
        raw_output
    )

    logger.debug(
        "Parsed combined output:\n%s",
        parsed_output,
    )

    verification_result = parsed_output.get(
        "verification_result"
    )

    if not verification_result:
        raise ValueError(
            "Parser did not return a verification_result "
            "for the combined submission."
        )

    # If verification failed, identify the source file referenced
    # by the counterexample.
    if verification_result == "FAILED":
        source_file = _find_counterexample_file(
            parsed_output,
            source_files,
        )
    else:
        # For a successful combined verification there is no
        # particular failing source file.
        source_file = source_files[0]

    result = await _build_result(
        source_file=source_file,
        raw_output=raw_output,
        parsed_output=parsed_output,
    )

    return [result]


async def _build_result(
    source_file: Path,
    raw_output: str,
    parsed_output: Dict[str, Any],
) -> Dict[str, Any]:
    """Convert parser output into the structure expected by the backend."""

    verification_result = parsed_output.get(
        "verification_result"
    )

    if not verification_result:
        raise ValueError(
            "Parser did not return verification_result "
            "for file '%s'. Parsed output: %r"
            % (
                source_file.name,
                parsed_output,
            )
        )

    entry: Dict[str, Any] = {
        "file": source_file.name,
        "verification_result": verification_result,
        "raw_output": raw_output,
        "counterexample": None,
        "feedback": None,
        "diagram": {
            "plantuml": "",
            "svg": "",
            "render_error": "",
        },
    }

    # Preserve the original pipeline behaviour:
    # only failed verification goes to the NLP module.
    if verification_result != "FAILED":
        logger.info(
            "No violation detected in %s; skipping feedback generation.",
            source_file.name,
        )

        return entry

    # The parser output itself is the counterexample consumed
    # by the NLP module.
    counterexample = dict(
        parsed_output
    )

    failing_line = counterexample.get(
        "line"
    )

    if failing_line:
        source = extract_snippet(
            source_file,
            failing_line,
        )

        logger.debug(
            "Extracted snippet for %s (lines 1-%s):\n%s",
            source_file.name,
            failing_line,
            source,
        )

    else:
        # Certain failure types may not contain a precise line.
        source = source_file.read_text(
            encoding="utf-8"
        )

        logger.debug(
            "No failing line for %s; supplying complete source.",
            source_file.name,
        )

    # Add the source to the parser output before giving it to
    # the NLP module.
    counterexample["source_snippet"] = source

    # Preserve this for the backend.
    entry["counterexample"] = counterexample

    logger.debug(
        "NLP input for %s:\n%s",
        source_file.name,
        counterexample,
    )

    try:
        client = LLMClient.from_env()

        generation_result = await client.generate_feedback(
            counterexample
        )

        entry["feedback"] = (
            generation_result.feedback.model_dump()
        )

        entry["diagram"] = {
            "plantuml": generation_result.diagram_plantuml,
            "svg": generation_result.diagram_svg,
            "render_error": (
                generation_result.diagram_render_error
            ),
        }

        logger.info(
            "Feedback generated successfully for %s.",
            source_file.name,
        )

    except Exception as error:
        # feedback.py explicitly checks for this field:
        #
        # "feedback_error" not in e
        #
        # so preserve the model-checker result even if NLP or
        # diagram generation fails.
        logger.exception(
            "Feedback generation failed for %s.",
            source_file.name,
        )

        entry["feedback_error"] = str(
            error
        )

    return entry


def _find_source_files(
    submission_dir: Path,
) -> List[Path]:
    """Find C++ source files in an uploaded submission."""

    supported_extensions = {
        ".cpp",
        ".cc",
        ".cxx",
        ".c++",
    }

    files = [
        path
        for path in submission_dir.rglob("*")
        if (
            path.is_file()
            and path.suffix.lower()
            in supported_extensions
        )
    ]

    return sorted(
        files,
        key=lambda path: str(path).lower(),
    )


def _find_counterexample_file(
    parsed_output: Dict[str, Any],
    source_files: List[Path],
) -> Path:
    """Match the parser's violated file back to an uploaded source file."""

    parser_file = str(
        parsed_output.get(
            "file",
            "",
        )
        or ""
    )

    if parser_file:
        parser_name = Path(
            parser_file.replace("\\", "/")
        ).name.lower()

        for source_file in source_files:
            if (
                source_file.name.lower()
                == parser_name
            ):
                return source_file

    # If the parser cannot identify the specific file,
    # use the first uploaded source as a safe fallback.
    return source_files[0]


def _is_combined_mode(
    mode: str,
) -> bool:
    """Determine whether the backend requested combined compilation."""

    normalized = (
        str(mode or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return normalized in {
        "combined",
        "combine",
        "project",
        "whole_project",
        "multi_file",
        "multifile",
        "together",
        "all",
    }


def _raise_if_checker_error(
    raw_output: str,
    source_file: Path,
) -> None:
    """Prevent model-checker execution errors from being treated as passes."""

    stripped = (
        raw_output or ""
    ).strip()

    if not stripped:
        raise RuntimeError(
            "ESBMC returned no output for %s."
            % source_file.name
        )

    if stripped.startswith("Error:"):
        raise RuntimeError(
            stripped
        )

# ======================================================================================================
# # Entry point for the end-to-end pipeline
# # Student Input → Model Checker → Parser → NLP Module → Feedback Output

# import asyncio
# import logging
# from pathlib import Path
# from typing import Any, Dict, List, Literal

# from pipeline.model_checker.esbmc_runner import ESBMCRunner
# from pipeline.parser.counterexample_parser import parse
# from pipeline.nlp.llm_client import LLMClient
# from pipeline.nlp.schemas import Counterexample
# from pipeline.snippet import extract_snippet

# logger = logging.getLogger(__name__)

# CompilationMode = Literal["independent", "combined"]


# def discover_source_files(submission_dir: Path) -> List[Path]:
#     return sorted(submission_dir.rglob("*.cpp"))


# async def _generate_feedback_for_entry(
#     entry: Dict[str, Any],
#     parsed: Dict[str, Any],
#     src_file: Path,
#     llm_client: LLMClient,
# ) -> None:
#     parsed.setdefault("tool", "esbmc")

#     try:
#         parsed["source_snippet"] = extract_snippet(src_file, parsed.get("line"))
#     except Exception:
#         logger.warning("Snippet extraction failed for %s; falling back to full file.", src_file)
#         try:
#             parsed["source_snippet"] = src_file.read_text(encoding="utf-8", errors="replace")
#         except OSError:
#             parsed["source_snippet"] = ""

#     try:
#         counterexample = Counterexample.model_validate(parsed)
#         generation_result = await llm_client.generate_feedback(counterexample)

#         entry["feedback"] = generation_result.feedback.model_dump()
#         entry["feedback_meta"] = {
#             "provider": generation_result.provider,
#             "model": generation_result.model,
#             "prompt_version": generation_result.prompt_version,
#             "used_fallback": generation_result.used_fallback,
#             "latency_ms": generation_result.latency_ms,
#         }
#         entry["counterexample"] = counterexample.model_dump()
#         entry["diagram"] = {
#             "plantuml": generation_result.diagram_plantuml,
#             "svg": generation_result.diagram_svg,
#             "render_error": generation_result.diagram_render_error,
#         }
#     except Exception as exc:
#         logger.error("Feedback generation failed for %s: %s", src_file, exc)
#         entry["feedback_error"] = str(exc)


# async def _run_independent(
#     submission_dir: Path,
#     source_files: List[Path],
#     checker: ESBMCRunner,
#     llm_client: LLMClient,
# ) -> List[Dict[str, Any]]:
#     """independent exercise"""
#     results: List[Dict[str, Any]] = []

#     for src_file in source_files:
#         logger.debug("Running model checker on: %s", src_file)
#         raw_output = await asyncio.to_thread(checker.run, src_file)
#         parsed = parse(raw_output)
#         verification_result = parsed.get("verification_result", "ERROR")

#         entry: Dict[str, Any] = {
#             "file": str(src_file.relative_to(submission_dir)),
#             "verification_result": verification_result,
#             "raw_output": raw_output,
#             "feedback": None,
#         }

#         if verification_result == "FAILED":
#             await _generate_feedback_for_entry(entry, parsed, src_file, llm_client)
#         else:
#             logger.info("No violation detected in %s; skipping feedback generation.", src_file)

#         results.append(entry)

#     return results


# async def _run_combined(
#     submission_dir: Path,
#     source_files: List[Path],
#     checker: ESBMCRunner,
#     llm_client: LLMClient,
# ) -> List[Dict[str, Any]]:
#     """All .cpp files together - one program"""
#     logger.debug("Running model checker on combined submission: %s", source_files)
#     raw_output = await asyncio.to_thread(checker.run, source_files)
#     parsed = parse(raw_output)
#     verification_result = parsed.get("verification_result", "ERROR")

#     violation_file = parsed.get("file", "")
#     try:
#         relative_violation_file = str(Path(violation_file).resolve().relative_to(submission_dir))
#     except (ValueError, OSError):
#         relative_violation_file = violation_file or "combined submission"

#     entry: Dict[str, Any] = {
#         "file": relative_violation_file,
#         "all_files": [str(f.relative_to(submission_dir)) for f in source_files],
#         "verification_result": verification_result,
#         "raw_output": raw_output,
#         "feedback": None,
#     }

#     if verification_result == "FAILED":
#         try:
#             target_file = Path(violation_file).resolve()
#             if not target_file.is_file():
#                 raise FileNotFoundError
#         except (FileNotFoundError, OSError):
#             target_file = source_files[0]
#             logger.warning(
#                 "Could not resolve violation file '%s'; falling back to %s for snippet.",
#                 violation_file, target_file,
#             )

#         await _generate_feedback_for_entry(entry, parsed, target_file, llm_client)
#     else:
#         logger.info("No violation detected across combined submission.")

#     return [entry]


# async def run_pipeline(
#     submission_dir: Path,
#     mode: CompilationMode = "independent",
# ) -> Dict[str, Any]:
#     submission_dir = Path(submission_dir).resolve()
#     if not submission_dir.is_dir():
#         raise FileNotFoundError(f"Submission directory not found: {submission_dir}")

#     source_files = discover_source_files(submission_dir)
#     if not source_files:
#         raise ValueError(f"No .cpp files found in {submission_dir}")

#     checker = ESBMCRunner()
#     llm_client = LLMClient.from_env()

#     if mode == "combined":
#         results = await _run_combined(submission_dir, source_files, checker, llm_client)
#     else:
#         results = await _run_independent(submission_dir, source_files, checker, llm_client)

#     return {"submission_dir": str(submission_dir), "mode": mode, "results": results}


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