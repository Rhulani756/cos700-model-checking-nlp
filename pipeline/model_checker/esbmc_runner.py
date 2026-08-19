<<<<<<< HEAD
import subprocess
from pathlib import Path
from typing import Union


class ESBMCRunner:
    def __init__(self, unwind_limit: int = 5, timeout_seconds: int = 30):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds
        # Updated for Linux / WSL:
        self.esbmc_path = "esbmc"

    def run(self, file_path: Union[str, Path]) -> str:
        file_path = Path(file_path).resolve()

        if not file_path.exists():
            return f"Error: File not found at {file_path}"

        cmd = [
            self.esbmc_path,
            str(file_path),
            "--unwind", str(self.unwind_limit),
            "--bounds-check",         # 1. Array out of bounds
            "--div-by-zero-check",    # 2. Division by zero
            "--pointer-check",        # 3. Null pointer safety
            "--compact-trace",        # Compact output for trace parsing
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
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
=======
import subprocess
from pathlib import Path
from typing import List,Union

class ESBMCRunner:
    def __init__(self, unwind_limit: int = 50, timeout_seconds: int = 60):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds
        self.esbmc_path = "esbmc"

    def run(self, file_paths: Union[str, Path, List[Union[str, Path]]]) -> str:
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        resolved = [Path(p).resolve() for p in file_paths]
        missing = [str(p) for p in resolved if not p.exists()]
        if missing:
            return f"Error: File(s) not found: {missing}"

        cmd = [
            self.esbmc_path,
            *[str(p) for p in resolved],
            "--unwind", str(self.unwind_limit),
            "--compact-trace",
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=self.timeout_seconds
            )
            output = (result.stdout or "") + (result.stderr or "")
            return output if output.strip() else "ESBMC executed with no output."
        except subprocess.TimeoutExpired:
            return f"Error: ESBMC verification timed out after {self.timeout_seconds} seconds."
        except FileNotFoundError:
            return f"Error: Could not find ESBMC binary at '{self.esbmc_path}'."
        except Exception as e:
            return f"Error executing ESBMC: {str(e)}"
        
# class ESBMCRunner:
#     def __init__(self, unwind_limit: int = 50, timeout_seconds: int = 60):
#         self.unwind_limit = unwind_limit
#         self.timeout_seconds = timeout_seconds
#         # Updated for Linux / WSL:
#         self.esbmc_path = "esbmc"

#     def run(self, file_path: Union[str, Path]) -> str:
#         file_path = Path(file_path).resolve()

#         if not file_path.exists():
#             return f"Error: File not found at {file_path}"

#         cmd = [
#             self.esbmc_path,
#             str(file_path),
#             "--unwind", str(self.unwind_limit),
#             "--compact-trace",        # Compact output for trace parsing
#         ]

#         try:
#             result = subprocess.run(
#                 cmd,
#                 capture_output=True,
#                 text=True,
#                 timeout=self.timeout_seconds
#             )
            
#             output = (result.stdout or "") + (result.stderr or "")
#             return output if output.strip() else "ESBMC executed with no output."

#         except subprocess.TimeoutExpired:
#             return f"Error: ESBMC verification timed out after {self.timeout_seconds} seconds."
#         except FileNotFoundError:
#             return f"Error: Could not find ESBMC binary at '{self.esbmc_path}'."
#         except Exception as e:
#             return f"Error executing ESBMC: {str(e)}"


if __name__ == "__main__":
    runner = ESBMCRunner()
>>>>>>> origin/feature/ui+pipeline
    print("ESBMCRunner initialized successfully.")