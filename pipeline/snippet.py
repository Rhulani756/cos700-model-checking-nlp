from pathlib import Path
from typing import Union


def extract_snippet(submission_path: Union[str, Path], failing_line: int) -> str:
    """
    Returns the source code from line 1 up to and including the failing line.

    Args:
        submission_path: Path to the student's submission.
        failing_line: 1-indexed line number where the model checker flagged the violation.
    """
    lines = Path(submission_path).read_text().splitlines()
    return "\n".join(lines[:failing_line])