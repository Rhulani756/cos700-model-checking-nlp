# Parses raw model checker output into a structured representation
import re

LOCATION_RE = re.compile(
    r"^file\s+(?P<file>.*?)\s+line\s+(?P<line>\d+)\s+column\s+(?P<column>\d+)\s+function\s+(?P<function>\S+)\s*$"
)

STATE_RE = re.compile(
    r"^State\s+(?P<state_number>\d+)\s+file\s+(?P<file>.*?)\s+line\s+(?P<line>\d+)"
    r"\s+column\s+(?P<column>\d+)(?:\s+function\s+(?P<function>\S+))?\s+thread\s+(?P<thread>\d+)\s*$"
)

def parse_location_line(raw_line: str) -> dict:
    m = LOCATION_RE.match(raw_line.strip())
    if not m:
        raise ValueError(f"Unrecognized location line format: {raw_line!r}")
    return {
        "file": m.group("file"),
        "line": int(m.group("line")),
        "column": int(m.group("column")),
        "function": m.group("function"),
    }

def parse_state_line(raw_line: str) -> dict:
    m = STATE_RE.match(raw_line.strip())
    if not m:
        raise ValueError(f"Unrecognized state line format: {raw_line!r}")
    return {
        "state_number": int(m.group("state_number")),
        "file": m.group("file"),
        "line": int(m.group("line")),
        "column": int(m.group("column")),
        "function": m.group("function"),  # may be None for library/global states
        "thread": int(m.group("thread")),
    }

def parse(raw_output: str) -> dict:
    # check that it is a failed verification case
    lines = raw_output.splitlines()
    # print(lines)
    result = {}

    for line in lines:
        if "VERIFICATION FAILED" in line:
            result["verification_result"] = "FAILED"
            break
        elif "VERIFICATION SUCCESSFUL" in line:
            result["verification_result"] = "SUCCESSFUL"
            break
        elif "VERIFICATION UNKNOWN" in line:
            result["verification_result"] = "UNKNOWN"
            break

    if result.get("verification_result") != "FAILED":
        return result

    state_begin_line = None

    # grab violated property information
    for i, line in enumerate(lines):
        if line.strip() == "[Counterexample]":
            state_begin_line = i + 3    # save the line number of the first state
        if line.strip() == "Violated property:":
            # line 2 — file/line/column/function
            loc = parse_location_line(lines[i + 1])
            result["file"] = loc["file"]
            result["line"] = loc["line"]
            result["column"] = loc["column"]
            result["function"] = loc["function"]

            # line 3 — violation type
            result["violation_type"] = lines[i + 2].strip()

            # line 4 — optional condition
            # if the third line is not empty
            if i + 3 < len(lines) and lines[i + 3].strip() != "":
                # save the additional information
                result["violation_description"] = lines[i + 3].strip()
            else:
                result["violation_description"] = None

            break

    result["states"] = []
    entry = {}

    # grab state information
    for i, line in enumerate(lines[state_begin_line:]):

        # print()
        # print("current line", line)
        # print()

        # get the first character on the line
        first_character = line[0] if line else ""

        if first_character == "S":
            state = parse_state_line(line)
            entry["state_number"] = state["state_number"]
            entry["line"] = state["line"]
            entry["function"] = state["function"]
        elif first_character == "-": # demarcator line, skip it
            continue
        elif first_character == "": # empty line that separates states, skip it
            continue
        elif first_character == "V": # violated property section, exit loop
            entry["assignment"] = None
            result["states"].append(entry)
            break
        else:
            assignment = line.strip()
            if " (" in assignment:
                assignment = assignment[:assignment.index(" (")]
            entry["assignment"] = assignment
            result["states"].append(entry)
            entry = {}
    return result