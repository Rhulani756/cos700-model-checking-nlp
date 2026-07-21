import subprocess
import json
from pathlib import Path
from typing import Union


class CBMCRunner:
    def __init__(self, unwind_limit: int = 5, timeout_seconds: int = 30):
        self.unwind_limit = unwind_limit
        self.timeout_seconds = timeout_seconds

    def run(self, file_path: Union[str, Path]) -> str:
        file_path = Path(file_path).resolve()
        
        if not file_path.exists():
            return f"Error: File not found at {file_path}"

        # Construct CBMC command with clean flags and structured JSON UI output
        cmd = [
            "cbmc",
            str(file_path),
            "--unwind", str(self.unwind_limit),
            "--bounds-check",
            "--div-by-zero-check",
            "--pointer-check",
            "--signed-overflow-check",
            "--json-ui"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            raw_stdout = result.stdout
        except subprocess.TimeoutExpired:
            return f"Error: CBMC verification timed out after {self.timeout_seconds} seconds."
        except Exception as e:
            return f"Error executing CBMC: {str(e)}"

        # Cleanly parse JSON output to strip away standard library noise
        return self._format_clean_output(raw_stdout)

    def _format_clean_output(self, raw_stdout: str) -> str:
        """Extracts strictly relevant property checks and failure traces from CBMC output."""
        try:
            data = json.loads(raw_stdout)
        except json.JSONDecodeError:
            # Fallback text filtering if JSON parsing fails
            return self._fallback_filter(raw_stdout)

        clean_lines = []
        
        for item in data:
            # Extract verification results and property checks
            if "result" in item:
                for res in item["result"]:
                    property_id = res.get("property", "Unknown Property")
                    status = res.get("status", "UNKNOWN").upper()
                    description = res.get("description", "")
                    location = res.get("location", {})
                    line = location.get("line", "?")
                    file = location.get("file", "")

                    line_fmt = f"[{property_id}] Line {line} {description}: {status}"
                    if file:
                        line_fmt += f" (File: {Path(file).name})"
                    clean_lines.append(line_fmt)

                    # Extract trace assignments for failures
                    if status == "FAILED" and "trace" in res:
                        clean_lines.append("\n  --- Failure Trace ---")
                        for step in res["trace"]:
                            if step.get("type") == "assignment":
                                lhs = step.get("lhs", "")
                                value = step.get("value", {}).get("binary", "") or step.get("value", {}).get("data", "")
                                step_line = step.get("location", {}).get("line", "?")
                                if lhs:
                                    clean_lines.append(f"  Line {step_line}: {lhs} = {value}")
                        clean_lines.append("  ---------------------")

            # Extract overall result status
            elif "messageType" in item and item["messageType"] == "status":
                text = item.get("text", "")
                if "VERIFICATION" in text:
                    clean_lines.append(f"\n{text}")

        if not clean_lines:
            return "No properties evaluated or no verification errors found."

        return "\n".join(clean_lines)

    def _fallback_filter(self, raw_text: str) -> str:
        """Fallback line filter if JSON output is unavailable."""
        lines = raw_text.splitlines()
        filtered = []
        for line in lines:
            if any(key in line for key in ["[main.", "VERIFICATION", "FAILED", "SUCCESSFUL", "division by zero"]):
                filtered.append(line)
        return "\n".join(filtered) if filtered else raw_text


if __name__ == "__main__":
    # Quick sanity check
    runner = CBMCRunner()
    print("CBMCRunner initialized successfully.")