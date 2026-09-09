import subprocess
import time
from pathlib import Path
from typing import List, Union, Tuple


class ESBMCRunner:
    def __init__(self, unwind_limit: int = 50, timeout_seconds: int = 60):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds
        self.esbmc_path = "esbmc"

    def run(self, file_paths: Union[str, Path, List[Union[str, Path]]]) -> Tuple[str, str]:
        """
        Runs ESBMC twice (singular-property trace + multi-property result-only)
        concurrently. Always returns a (output1, output2) tuple — on any
        infrastructure failure (missing file, timeout, missing binary, etc.),
        both slots are set to the same "Error: ..." string so callers can
        detect failure without needing a separate return shape.
        """
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        resolved = [Path(p).resolve() for p in file_paths]
        missing = [str(p) for p in resolved if not p.exists()]
        if missing:
            err = f"Error: File(s) not found: {missing}"
            return err, err

        cmd = [
            self.esbmc_path,
            *[str(p) for p in resolved],
            "--unwind", str(self.unwind_limit),
            "--compact-trace",
        ]

        cmd2 = [
            self.esbmc_path,
            *[str(p) for p in resolved],
            "--quiet",
            "--unwind", str(self.unwind_limit),
            "--multi-property",
            "--result-only",
            "--no-align-check",
        ]

        proc1 = None
        proc2 = None
        try:
            proc1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            proc2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            deadline = time.monotonic() + self.timeout_seconds

            remaining1 = max(0.0, deadline - time.monotonic())
            stdout1, stderr1 = proc1.communicate(timeout=remaining1)

            remaining2 = max(0.0, deadline - time.monotonic())
            stdout2, stderr2 = proc2.communicate(timeout=remaining2)

            output1 = (stdout1 or "") + (stderr1 or "")
            output2 = (stdout2 or "") + (stderr2 or "")

            return output1, output2

        except subprocess.TimeoutExpired:
            err = f"Error: ESBMC verification timed out after {self.timeout_seconds} seconds."
            return err, err
        except FileNotFoundError:
            err = f"Error: Could not find ESBMC binary at '{self.esbmc_path}'."
            return err, err
        except Exception as e:
            err = f"Error executing ESBMC: {str(e)}"
            return err, err
        finally:
            for proc in (proc1, proc2):
                if proc is not None and proc.poll() is None:
                    proc.kill()
                    proc.wait()


if __name__ == "__main__":
    runner = ESBMCRunner()
    print("ESBMCRunner initialized successfully.")

# import subprocess
# from pathlib import Path
# from typing import List,Union

# class ESBMCRunner:
#     def __init__(self, unwind_limit: int = 50, timeout_seconds: int = 60):
#         self.unwind_limit = unwind_limit
#         self.timeout_seconds = timeout_seconds
#         self.esbmc_path = "esbmc"

#     def run(self, file_paths: Union[str, Path, List[Union[str, Path]]]) -> str:
#         if isinstance(file_paths, (str, Path)):
#             file_paths = [file_paths]

#         resolved = [Path(p).resolve() for p in file_paths]
#         missing = [str(p) for p in resolved if not p.exists()]
#         if missing:
#             return f"Error: File(s) not found: {missing}"

#         cmd = [
#             self.esbmc_path,
#             *[str(p) for p in resolved],
#             "--unwind", str(self.unwind_limit),
#             "--compact-trace",
#         ]

#         try:
#             result = subprocess.run(
#                 cmd, capture_output=True, text=True, timeout=self.timeout_seconds
#             )
#             output = (result.stdout or "") + (result.stderr or "")
#             return output if output.strip() else "ESBMC executed with no output."
#         except subprocess.TimeoutExpired:
#             return f"Error: ESBMC verification timed out after {self.timeout_seconds} seconds."
#         except FileNotFoundError:
#             return f"Error: Could not find ESBMC binary at '{self.esbmc_path}'."
#         except Exception as e:
#             return f"Error executing ESBMC: {str(e)}"

# if __name__ == "__main__":
#     runner = ESBMCRunner()
#     print("ESBMCRunner initialized successfully.")