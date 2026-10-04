# Parses raw model checker outputs into structured representations
import re

class ESBMCParser:
    def __init__(self,
                 location_re = re.compile(r"^file\s+(?P<file>.*?)\s+line\s+(?P<line>\d+)\s+column\s+(?P<column>\d+)\s+function\s+(?P<function>\S+)\s*$"),
                 state_re = re.compile(
            r"^State\s+(?P<state_number>\d+)\s+file\s+(?P<file>.*?)\s+line\s+(?P<line>\d+)"
            r"\s+column\s+(?P<column>\d+)(?:\s+function\s+(?P<function>\S+))?\s+thread\s+(?P<thread>\d+)\s*$"
        )):

        self.LOCATION_RE = location_re

        self.STATE_RE = state_re

        self.PROPERTIES = {
                "unwinding assertion",
                "array bounds violated",
                "division by zero",
                "dereference failure: NULL pointer"
        }

    def parse_location_line(self, raw_line: str) -> dict:
        """
        Parses a location line from the model checker output.
        :param raw_line:
        :return: Dict containing filename, line, column, and function of the program
        """
        m = self.LOCATION_RE.match(raw_line.strip())
        if not m:
            raise ValueError(f"Unrecognized location line format: {raw_line!r}")
        return {
            "file": m.group("file"),
            "line": int(m.group("line")),
            "column": int(m.group("column")),
            "function": m.group("function"),
        }

    def parse_state_line(self, raw_line: str) -> dict:
        """
        Parses a state line from the model checker output.
        :param raw_line:
        :return: Dict containing state number, filename, line, column, function, and thread
        """
        m = self.STATE_RE.match(raw_line.strip())

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

    def parse_singular(self, lines: list) -> dict:
        """
        Parses the model checker output for single property verification.
        :param lines:
        :return: Dict containing the verification result, filename, line, column, function, violation type, violation description, and states
        """

        # default to UNKNOWN verification result if the model checker returned anything other than FAILED or SUCCESSFUL
        result = {}
        result["verification_result"] = "UNKNOWN"

        for line in lines:
            if "VERIFICATION FAILED" in line:
                result["verification_result"] = "FAILED"
                break
            elif "VERIFICATION SUCCESSFUL" in line:
                result["verification_result"] = "SUCCESSFUL"
                break

        # only failed verifications have counterexamples
        if result.get("verification_result") != "FAILED":
            return result

        state_begin_line = None

        # grab violated property information
        for i, line in enumerate(lines):

            if line.strip() == "[Counterexample]":
                # save the line number of the first state
                state_begin_line = i + 3

            if line.strip() == "Violated property:":
                # line 2 — file/line/column/function
                i += 1
                loc = self.parse_location_line(lines[i])
                result["file"] = loc["file"]
                result["line"] = loc["line"]
                result["column"] = loc["column"]
                result["function"] = loc["function"]

                # line 3 — violation type
                i += 1
                violation_type = lines[i].strip()

                result["violation_type"] = violation_type

                # "array bounds violated", "dereference failure: NULL pointer", "unwinding assertion", "division by zero"
                if not any(prop in violation_type for prop in self.PROPERTIES):
                    result["verification_result"] = "UNSUPPORTED"
                    return result

                # default violation description to None
                result["violation_description"] = None
                i += 1

                while i < len(lines) and lines[i].strip() and "VERIFICATION" not in lines[i]:
                    line = lines[i].strip()

                    # ignore CWE lines
                    if line.startswith("CWE"):
                        pass
                    else:
                        # save the violation description
                        result["violation_description"] = line
                    i += 1

                break

        result["states"] = []
        entry = {}

        if state_begin_line is None:
            raise ValueError("Expected '[Counterexample]' marker but none was found")

        i = state_begin_line
        # grab state information
        # for i, line in enumerate(lines[state_begin_line:]):
        while i < len(lines):
            line = lines[i]
            # get the first character on the line
            first_character = line[0] if line else ""

            if first_character == "S":
                state = self.parse_state_line(line)

                entry["state_number"] = state["state_number"]
                entry["line"] = state["line"]
                entry["function"] = state["function"]
                # i += 1
            elif first_character == "-":  # demarcator line
                # continue
                # next line is the beginning of assignment lines
                i += 1

                first_character = lines[i][0] if lines[i] else ""

                if first_character == "V":  # violated property section, exit loop
                    entry["assignment"] = None
                    result["states"].append(entry)
                    break  # exit the loop
                else:
                    assignment_lines = [lines[i].strip()]

                    i += 1
                    while i < len(lines) and lines[i].strip() != "":
                        assignment_lines.append(lines[i].strip())
                        i += 1

                    assignment = "\n".join(assignment_lines)

                    if "{" in assignment:
                        pass
                    elif "(" in assignment:
                        # ignore everything after first parenthesis
                        assignment = assignment[:assignment.index(" (")]

                    entry["assignment"] = assignment

                result["states"].append(entry)
                entry = {}

            i += 1

        return result

    def extract_result(self, target: str, lines: list[str]) -> set[str]:
        """
        Extracts the properties from the lines that contain the target string.
        :param target:
        :param lines:
        :return: 1-indexed set of properties that have passed or failed verification
        """
        result_set = set()

        # iterate through the lines and extract the properties
        for line in lines:
            if target in line:

                # loop through the set of properties and add the one that is found
                for prop in self.PROPERTIES:
                    if prop in line:
                        result_set.add(prop)
                        break

        return result_set

    def passed_properties(self, lines: list) -> set[str]:
        """
        Returns a set of properties that have passed verification.
        :param lines:
        :return: 1-indexed set of properties that have passed verification
        """

        target = "PASSED:"

        # get the set of properties that have passed verification
        passed_set = self.extract_result(target, lines)

        return passed_set

    def failed_properties(self, lines: list) -> set[str]:
        """
        Returns a set of properties that have failed verification.
        :param lines:
        :return: 1-indexed set of properties that have failed verification
        """

        target = "FAILED:"

        # get the set of properties that have failed verification
        failed_set = self.extract_result(target, lines)

        return failed_set

    def undetermined_cases(self, passed_set: set[str], failed_set: set[str]) -> set[str]:
        """
        Properties for which the model checker does not report a PASSED or FAILED result.
        Either the model checker did not have to check it (e.g. no division is performed in the program, so division-by-zero is not reported),
        or it did not report on a PASSED claim.
        :param passed_set:
        :param failed_set:
        :return: A set of properties that are not present in either the passed or failed sets
        """

        # get the union of the two sets (passed and failed)
        present_properties = passed_set.union(failed_set)

        # get the difference between the two sets (cases that are not present in either set)
        undetermined = self.PROPERTIES.difference(present_properties)

        return undetermined

    @staticmethod
    def rename_properties(properties: set[str]):
        """
        Rename properties in the sets for readability in the front-end
        :param properties:
        :return:
        """

        if "dereference failure: NULL pointer" in properties:
            properties.remove("dereference failure: NULL pointer")
            properties.add("null pointer dereference")
        if "array bounds violated" in properties:
            properties.remove("array bounds violated")

            properties.add("array bounds")

        # "unwinding assertion" and "division by zero" are left as-is

        return

    def parse_multi(self, lines: list) -> dict:
        """
        Parses the model checker output for multi-property verification.
        :param lines:
        :return: Dict containing the set of passed, failed, and undetermined properties
        """
        result = {}

        # retrieve the set of passed properties
        passed = self.passed_properties(lines)

        # retrieve the set of failed properties
        failed = self.failed_properties(lines)

        # retrieve the set of undetermined (no passed or failed output) properties
        undetermined = self.undetermined_cases(passed, failed)

        # remove failed properties from passed and undetermined sets. failed properties take precedence
        passed.difference_update(failed)
        undetermined.difference_update(failed)

        # rename properties in all three sets to make them more readable for the front-end
        self.rename_properties(passed)
        self.rename_properties(failed)
        self.rename_properties(undetermined)

        # save the results
        result["passed"] = list(passed)
        result["failed"] = list(failed)
        result["undetermined"] = list(undetermined)

        return result

    def parse(self, raw_output: str, raw_multi_output: str) -> str | tuple[dict, dict]:
        """
        Parses the raw output from the model checker into structured data.
        :param raw_multi_output:
        :param raw_output:
        :return: 2 dictionaries, one for singular property output and one for passed / failed / undetermined properties
        """

        singular = {}
        multi = {}

        # split the output from singular property verification into a list of lines
        if raw_output != "":
            lines = raw_output.splitlines()

            singular = self.parse_singular(lines)

        # split the output from multi-property verification into a list of lines
        if raw_multi_output != "":
            lines_multi = raw_multi_output.splitlines()

            multi = self.parse_multi(lines_multi)

        return singular, multi