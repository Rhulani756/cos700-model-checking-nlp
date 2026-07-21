import subprocess
from pathlib import Path

class CBMCRunner:
    def __init__(self, unwind_limit: int = 5, timeout_seconds: int = 30):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds

    def run(self, file_path: Path) -> str:
        """
        Invokes CBMC on a specific C++ file and captures its stdout/stderr streams.
        """
        if not file_path.exists():
            return f"Error: Target file {file_path} does not exist."

        # Production execution arguments for loop and upper/lower bound checking
        command = [
            "cbmc", 
            str(file_path), 
            "--unwind", str(self.unwind_limit), 
            "--unwinding-assertions"
        ]

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Capture parsing or compiler issues in stdout
                text=True,
                timeout=self.timeout_seconds
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            return f"Verification timed out after {self.timeout_seconds} seconds (Potential state space explosion).\n"
        except FileNotFoundError:
            return "Error: The 'cbmc' binary was not found on the system host PATH."