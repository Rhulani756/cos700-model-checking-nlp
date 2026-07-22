import subprocess
from pathlib import Path
from typing import Union


class CBMCRunner:
    def __init__(self, unwind_limit: int = 15, timeout_seconds: int = 30):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds
        self.cbmc_path = "cbmc"

    def run(self, file_path: Union[str, Path]) -> str:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            return f"Error: File not found at {file_path}"

        cmd = [
            self.cbmc_path,
            str(file_path),
            "--unwind", str(self.unwind_limit),
            "--no-unwinding-assertions",  # Don't fail just because a loop terminates at the bound
            "--bounds-check",             # Check for out-of-bounds array access
            "--pointer-check",            # Check for invalid pointer dereferences
            "--div-by-zero-check"         # Check for division by zero
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            
            output = (result.stdout or "") + (result.stderr or "")
            return output if output.strip() else "CBMC executed with no output."

        except subprocess.TimeoutExpired:
            return f"Error: CBMC verification timed out after {self.timeout_seconds} seconds."
        except FileNotFoundError:
            return f"Error: Could not find CBMC binary at '{self.cbmc_path}'."
        except Exception as e:
            return f"Error executing CBMC: {str(e)}"