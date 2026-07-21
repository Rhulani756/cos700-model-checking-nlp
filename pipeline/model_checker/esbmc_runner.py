import subprocess
from pathlib import Path
from typing import Union


class ESBMCRunner:
    def __init__(self, unwind_limit: int = 5, timeout_seconds: int = 30):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds
        # Direct path to esbmc binary
        self.esbmc_path = r"C:\Tools\ESBMC\bin\esbmc.exe"

    def run(self, file_path: Union[str, Path]) -> str:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            return f"Error: File not found at {file_path}"

        cmd = [
            self.esbmc_path,
            str(file_path),
            "--unwind", str(self.unwind_limit),
            "--compact-trace",      # Compact trace for parser teammate
            "--overflow-check",
            # Bypass MSVC STL compiler version assertion check
            "-D_ALLOW_COMPILER_AND_STL_VERSION_MISMATCH",
            "-D_CRT_SECURE_NO_WARNINGS"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            
            # Combine stdout and stderr as requested by parser teammate
            output = (result.stdout or "") + (result.stderr or "")
            return output if output.strip() else "ESBMC executed with no output."

        except subprocess.TimeoutExpired:
            return f"Error: ESBMC verification timed out after {self.timeout_seconds} seconds."
        except FileNotFoundError:
            return f"Error: Could not find ESBMC binary at '{self.esbmc_path}'."
        except Exception as e:
            return f"Error executing ESBMC: {str(e)}"


if __name__ == "__main__":
    runner = ESBMCRunner()
    print("ESBMCRunner initialized successfully.")