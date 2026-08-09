# Entry point for the end-to-end pipeline
# Student Input → Model Checker → Parser → NLP Module → Feedback Output

import logging
from pathlib import Path
from typing import Any, Dict, Union

from model_checker.esbmc_runner import ESBMCRunner
from parser.counterexample_parser import parse
from snippet import extract_snippet

logger = logging.getLogger(__name__)

PIPELINE_DIR = Path(__file__).resolve().parent
PROGRAMS_DIR = PIPELINE_DIR.parent / "data" / "programs"

runner = ESBMCRunner()


def run_pipeline(submission_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Executes the model checking pipeline.

    Args:
        submission_path: Path to the student's C++ submission.

    Returns:
        <tbd>
    """
    logger.debug("Running model checker on: %s", submission_path)
    raw_output = runner.run(submission_path)
    logger.debug("Raw model checker output:\n%s", raw_output)

    parsed_output = parse(raw_output)
    logger.debug("Parsed output:\n%s", parsed_output)

    if parsed_output.get("verification_result") != "FAILED":
        logger.info("No violation detected; skipping feedback generation.")
        return parsed_output

    snippet = extract_snippet(submission_path, parsed_output["line"])
    logger.debug("Extracted snippet (lines 1-%d):\n%s", parsed_output["line"], snippet)

    # result = client.generate_feedback_sync(parsed_output, snippet)

    return parsed_output # TODO change to "result" later


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s") # change INFO to DEBUG to see raw esbmc output and parsed output
    run_pipeline(PROGRAMS_DIR / "array_bounds" / "array_bounds_01_student_grades.cpp")
    # run_pipeline(PROGRAMS_DIR / "div_zero" / "<file_name_here>.cpp")
    # run_pipeline(PROGRAMS_DIR / "infinite_loop" / "<file_name_here>.cpp")
    # run_pipeline(PROGRAMS_DIR / "null_pointer" / "<file_name_here>.cpp")
