# Parser-to-NLP Interface Contract

## Purpose

This document defines the data contract between the counterexample parser and the NLP feedback module.

The parser is responsible for converting raw CBMC or ESBMC output into a structured Python dictionary. The NLP module consumes that dictionary, validates and normalises it, builds the property-specific LLM prompt, and returns structured pedagogical feedback.

No intermediate JSON file is required.

```text
Raw CBMC / ESBMC output
          |
          v
Counterexample parser
          |
          | Python dictionary
          v
LLMClient.generate_feedback(...)
          |
          v
Structured pedagogical feedback
```

## NLP entry points

For synchronous pipeline or command-line code:

```python
from pipeline.nlp.llm_client import LLMClient

client = LLMClient.from_env()
result = client.generate_feedback_sync(parser_output)
```

For asynchronous code such as a FastAPI route:

```python
from pipeline.nlp.llm_client import LLMClient

client = LLMClient.from_env()
result = await client.generate_feedback(parser_output)
```

`parser_output` may be either:

- a Python `dict`; or
- an already validated `Counterexample` object from `pipeline.nlp.schemas`.

## Canonical parser output

The parser should preferably return the following structure:

```python
{
    "violation_type": "array_bounds",
    "tool": "cbmc",
    "property_id": "main.array_bounds.1",
    "message": "array upper bound violated",
    "file": "submission.cpp",
    "line": 7,
    "function": "main",
    "source_snippet": "int values[5]; ...",
    "trace": [
        {
            "step": 1,
            "event": "Loop condition evaluated to true",
            "file": "submission.cpp",
            "line": 5,
            "function": "main",
            "thread": "",
            "variables": [
                {
                    "name": "i",
                    "value": "5",
                    "data_type": "int"
                }
            ]
        },
        {
            "step": 2,
            "event": "Array upper bound violated",
            "file": "submission.cpp",
            "line": 7,
            "function": "main",
            "thread": "",
            "variables": [
                {
                    "name": "i",
                    "value": "5",
                    "data_type": "int"
                }
            ]
        }
    ],
    "metadata": {
        "checker_version": "optional",
        "raw_property_class": "optional"
    }
}
```

## Field requirements

### Top-level counterexample fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `violation_type` | `str` | Yes | Logical-error category. Use one of the four canonical values listed below. |
| `message` | `str` | Yes | Non-empty checker failure message or concise parser-generated description. |
| `tool` | `str` | No | `cbmc`, `esbmc`, or `unknown`. Defaults to `unknown`. |
| `property_id` | `str` | No | Checker property identifier when available. |
| `file` | `str` | No | Source filename associated with the violation. |
| `line` | `int` or `None` | No | One-based source line number. Must be at least `1` when provided. |
| `function` | `str` | No | Function in which the violation occurs. |
| `source_snippet` | `str` | No | Relevant source-code excerpt. Supplying this significantly improves feedback quality. |
| `trace` | `list` | No | Ordered counterexample steps. Defaults to an empty list. |
| `metadata` | `dict` | No | Checker-specific information not represented by the canonical fields. |

Only `violation_type` and `message` are strictly required by the NLP schema. However, the parser should provide the source location, source snippet, and trace whenever available because these fields allow the LLM to explain the actual execution path rather than only restating the checker label.

### Supported violation types

Use these canonical values:

```text
array_bounds
null_safety
loop_termination
division_by_zero
```

The NLP module also recognises the following aliases, but the parser should prefer the canonical names.

| Canonical value | Recognised aliases |
|---|---|
| `array_bounds` | `array_bound`, `bounds`, `out_of_bounds`, `array_out_of_bounds`, `buffer_overflow` |
| `null_safety` | `null_pointer`, `null_dereference`, `nullptr_dereference`, `pointer_dereference` |
| `loop_termination` | `termination`, `non_termination`, `unwinding_assertion`, `loop_unwinding` |
| `division_by_zero` | `divide_by_zero`, `div_by_zero`, `zero_division` |

Hyphens and spaces are normalised to underscores. For example, `division-by-zero` and `division by zero` are accepted.

### Trace-step fields

Each entry in `trace` should use this structure:

```python
{
    "step": 0,
    "event": "Description of the state change or violation",
    "file": "submission.cpp",
    "line": 12,
    "function": "main",
    "thread": "0",
    "variables": [
        {
            "name": "divisor",
            "value": "0",
            "data_type": "int"
        }
    ]
}
```

| Field | Type | Required | Description |
|---|---|---:|---|
| `step` | `int` | Yes | Non-negative step number. |
| `event` | `str` | Yes | Non-empty description of what occurs at this step. |
| `file` | `str` | No | Source filename for the step. |
| `line` | `int` or `None` | No | One-based source line number. |
| `function` | `str` | No | Function active at this step. |
| `thread` | `str` | No | Thread identifier for concurrent traces. |
| `variables` | `list` | No | Variable values associated with this state. |

The trace must be chronological. The final steps should be the steps closest to the property violation.

### Trace-variable fields

| Field | Type | Required | Description |
|---|---|---:|---|
| `name` | `str` | Yes | Non-empty variable name. |
| `value` | Any scalar converted to `str` | No | Value shown by the model checker. |
| `data_type` | `str` | No | C or C++ data type when available. |

The parser may also provide variables as a dictionary:

```python
"variables": {
    "i": 5,
    "array_size": 5
}
```

The NLP schema automatically converts that mapping into the canonical list representation.

## Accepted field aliases

The NLP module accepts several aliases to reduce coupling between the parser and NLP implementations.

### Top-level aliases

| Canonical field | Accepted aliases |
|---|---|
| `violation_type` | `property_type`, `error_type`, `property` |
| `property_id` | `property_name`, `propertyId` |
| `message` | `description`, `failure_message`, `reason` |
| `file` | `source_file`, `filename` |
| `line` | `line_number` |
| `function` | `function_name` |
| `source_snippet` | `code_snippet`, `source` |
| `trace` | `counterexample`, `steps` |
| `tool` | `model_checker` |

### Trace-step aliases

| Canonical field | Accepted aliases |
|---|---|
| `step` | `step_number`, `index` |
| `event` | `description`, `action`, `kind` |
| `file` | `source_file`, `filename` |
| `line` | `line_number` |
| `function` | `function_name` |
| `thread` | `thread_id` |

### Trace-variable aliases

| Canonical field | Accepted aliases |
|---|---|
| `data_type` | `type` |

These aliases are compatibility features. New parser code should use the canonical field names so the interface remains clear and predictable.

## Minimum valid parser output

This is the smallest valid input:

```python
{
    "violation_type": "division_by_zero",
    "message": "division by zero"
}
```

It will be accepted, but the generated feedback will have limited evidence and may receive low confidence.

## Recommended outputs for each property

### Array bounds

Important evidence includes:

- array size;
- failing index value;
- valid index range;
- loop boundary or index calculation;
- line containing the array access.

```python
{
    "violation_type": "array_bounds",
    "message": "array upper bound violated",
    "line": 7,
    "source_snippet": "int values[5]; for (int i = 0; i <= 5; ++i) values[i] = i;",
    "trace": [
        {
            "step": 1,
            "event": "array write violates upper bound",
            "line": 7,
            "variables": {"i": 5, "array_size": 5}
        }
    ]
}
```

### Null safety

Important evidence includes:

- pointer name;
- pointer value or null state;
- branch that allowed the pointer to remain null;
- dereference line.

```python
{
    "violation_type": "null_safety",
    "message": "dereference failure: pointer is null",
    "line": 11,
    "trace": [
        {
            "step": 4,
            "event": "pointer dereferenced while null",
            "line": 11,
            "variables": {"node": "NULL"}
        }
    ]
}
```

### Loop termination

Important evidence includes:

- loop condition;
- controlling variables;
- values across several iterations;
- updates that fail to move the state toward termination;
- unwinding assertion or configured bound.

```python
{
    "violation_type": "loop_termination",
    "message": "unwinding assertion loop.0 failed",
    "line": 6,
    "trace": [
        {
            "step": 8,
            "event": "loop condition remains true",
            "line": 6,
            "variables": {"i": 0}
        }
    ],
    "metadata": {"unwind_bound": 10}
}
```

### Division by zero

Important evidence includes:

- divisor expression;
- final divisor value;
- branch or calculation that produced zero;
- division line.

```python
{
    "violation_type": "division_by_zero",
    "message": "division by zero",
    "line": 9,
    "trace": [
        {
            "step": 5,
            "event": "division evaluated with zero divisor",
            "line": 9,
            "variables": {"total": 12, "count": 0}
        }
    ]
}
```

## Validation behaviour

The NLP module validates parser output before contacting the LLM.

The following conditions cause validation to fail:

- missing `violation_type`;
- unsupported violation type;
- missing or blank `message`;
- `line` less than `1`;
- trace step less than `0`;
- blank trace-step `event`;
- blank trace-variable `name`.

The parser developer can validate output independently with:

```python
from pydantic import ValidationError
from pipeline.nlp.schemas import Counterexample

try:
    validated = Counterexample.model_validate(parser_output)
    print(validated.model_dump())
except ValidationError as error:
    print(error)
```

## Integration example

The parser should expose a function or method that returns a dictionary:

```python
class CounterexampleParser:
    def parse(self, raw_output: str) -> dict:
        # Parse CBMC or ESBMC output here.
        return {
            "violation_type": "array_bounds",
            "tool": "cbmc",
            "message": "array upper bound violated",
            "file": "submission.cpp",
            "line": 7,
            "trace": []
        }
```

The pipeline integration is then:

```python
from pipeline.nlp.llm_client import LLMClient
from pipeline.parser.counterexample_parser import CounterexampleParser

parser = CounterexampleParser()
client = LLMClient.from_env()

parser_output = parser.parse(raw_checker_output)
feedback_result = client.generate_feedback_sync(parser_output)

feedback_dict = feedback_result.model_dump()
```

For FastAPI or another asynchronous caller:

```python
parser_output = parser.parse(raw_checker_output)
feedback_result = await client.generate_feedback(parser_output)
```

## Output returned by the NLP module

The parser does not need to produce this structure, but it may be useful for integration testing. The NLP module returns:

```python
{
    "feedback": {
        "title": "...",
        "summary": "...",
        "root_cause": "...",
        "evidence": ["..."],
        "execution_path": ["..."],
        "why_it_matters": "...",
        "suggested_changes": ["..."],
        "example_fix": "...",
        "check_your_understanding": "...",
        "confidence": "high"
    },
    "provider": "gemini",
    "model": "...",
    "prompt_version": "1.0.0",
    "used_fallback": False,
    "latency_ms": 850
}
```

## Parser implementation recommendations

1. Preserve the original checker message instead of replacing it with a generic label.
2. Return trace steps in execution order.
3. Include the last state immediately before the violation.
4. Include only variables relevant to the violation where practical.
5. Convert checker-specific property names into one of the four canonical violation types.
6. Keep checker-specific information in `metadata` rather than adding many incompatible top-level fields.
7. Include a focused source snippet around the failing line rather than the entire submission.
8. Do not save the parsed structure to a JSON file unless another project requirement specifically needs persistence.

## Contract test

The parser developer can use the following test to confirm compatibility without making an LLM API request:

```python
from pipeline.nlp.schemas import Counterexample

parser_output = {
    "violation_type": "array_bounds",
    "tool": "cbmc",
    "message": "array upper bound violated",
    "file": "submission.cpp",
    "line": 7,
    "trace": [
        {
            "step": 1,
            "event": "array write violates upper bound",
            "line": 7,
            "variables": {"i": 5, "array_size": 5}
        }
    ]
}

validated = Counterexample.model_validate(parser_output)
assert validated.violation_type.value == "array_bounds"
assert validated.trace[0].variables[0].name == "i"
print("Parser output is compatible with the NLP module.")
```
