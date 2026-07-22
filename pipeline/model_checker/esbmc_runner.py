import os
import subprocess
from pathlib import Path
from typing import Union


class ESBMCRunner:
    def __init__(self, unwind_limit: int = 5, timeout_seconds: int = 30):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds
        self.esbmc_path = r"C:\Tools\ESBMC\bin\esbmc.exe"

    def run(self, file_path: Union[str, Path]) -> str:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            return f"Error: File not found at {file_path}"

        # 1. Environment configuration equivalent to Linux CPLUS_INCLUDE_PATH
        env = os.environ.copy()
        esbmc_base = Path(self.esbmc_path).parent.parent
        esbmc_include = esbmc_base / "include"

        if esbmc_include.exists():
            env["CPLUS_INCLUDE_PATH"] = str(esbmc_include)
            env["C_INCLUDE_PATH"] = str(esbmc_include)

        # 2. ESBMC execution flags
        cmd = [
            self.esbmc_path,
            str(file_path),
            "--unwind", str(self.unwind_limit),
            "--compact-trace",
            "--overflow-check",
            "--no-library",   # Ignores native MSVC library headers that cause STL1000 errors
            # Direct preprocessor define passed to Clang to bypass MSVC version assertions
            "-D_ALLOW_COMPILER_AND_STL_VERSION_MISMATCH"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                env=env
            )
            
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