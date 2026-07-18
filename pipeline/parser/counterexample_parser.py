# Parses raw model checker output into a structured representation

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
            location_line = lines[i + 1].strip().split()
            result["file"] = location_line[1]
            result["line"] = int(location_line[3])
            result["column"] = int(location_line[5])
            result["function"] = location_line[7]

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
        state_line = line.split()

        if first_character == "S":

            # print("state line", state_line)
            entry["state_number"] = int(state_line[1])
            entry["line"] = int(state_line[5])
            entry["function"] = state_line[9]
        elif first_character == "-": # demarcator line, skip it
            continue
        elif first_character == "": # empty line that separates states, skip it
            continue
        elif first_character == "V": # violated property section, exit loop
            entry["assignment"] = None
            result["states"].append(entry)
            break
        else:
            entry["assignment"] = line.strip()
            result["states"].append(entry)
            entry = {}
    return result
