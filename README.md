# Integrating Model Checking and NLP to Provide Pedagogic Feedback on Programming Assignments

## Overview

Automated assessment tools in programming education typically produce pass/fail feedback that fails to explain the root cause of logical errors. This project addresses that gap by combining **bounded model checking** with **natural language processing** to generate clear, pedagogically meaningful feedback on student C++ submissions.

The system runs student code through a formal verification tool (CBMC or ESBMC), parses the counterexample output into a structured representation, and passes it to a large language model that produces a human-readable explanation of the error targeted at novice programmers.

---

## Pipeline

```
Student Input → Model Checker → Parser → NLP Module → Feedback Output
```

| Stage | Description |
|---|---|
| **Student Input** | Raw C++ submission accepted by the system |
| **Model Checker** | CBMC or ESBMC verifies correctness properties and produces counterexamples |
| **Parser** | Extracts structured error information from raw model checker output |
| **NLP Module** | Constructs a prompt from the structured counterexample and queries an LLM |
| **Feedback Output** | Human-readable pedagogical explanation returned to the student |

---

## Verification Properties

The system targets four classes of logical errors common in introductory programming:

- **Array bounds** — out-of-bounds array access
- **Null safety** — null pointer dereferences
- **Loop termination** — non-terminating or incorrectly bounded loops
- **Division by zero** — arithmetic errors under specific execution paths

---

## Repository Structure

```
cos700-model-checking-nlp/
├── pipeline/
│   ├── main.py                            # End-to-end pipeline runner
│   ├── model_checker/
│   │   ├── cbmc_runner.py                 # CBMC invocation & output capture
│   │   ├── esbmc_runner.py                # ESBMC invocation & output capture
│   │   └── properties/                    # Verification property specs
│   │       ├── array_bounds.h
│   │       ├── null_safety.h
│   │       ├── loop_termination.h
│   │       └── division_by_zero.h
│   ├── parser/
│   │   └── counterexample_parser.py       # Raw trace → structured JSON
│   ├── nlp/
│   │   ├── llm_client.py                  # LLM prompt construction & querying
│   │   └── prompts/                       # Per-property prompt templates
│   │       ├── array_bounds.txt
│   │       ├── null_safety.txt
│   │       ├── loop_termination.txt
│   │       └── division_by_zero.txt
│   └── feedback/
│       └── formatter.py                   # Formats output for student
│
├── data/
│   ├── submissions/                       # Anonymised C++ programs
│   │   ├── correct/
│   │   └── incorrect/
│   │       ├── array_bounds/
│   │       ├── null_safety/
│   │       ├── loop_termination/
│   │       └── division_by_zero/
│   └── model_checker_outputs/             # Raw traces saved per tool
│       ├── cbmc/
│       └── esbmc/
│
├── evaluation/                            # Section 4.4 — evaluation study
│   ├── questionnaire/
│   ├── results/
│   └── scripts/
│
├── reports/                               # Final research report
├── docs/
│   └── proposal.pdf
├── requirements.txt
└── README.md
```

---

## Setup

> Full setup instructions will be added in Milestone 2 once the environment is configured.

### Prerequisites

- Python 3.10+
- CBMC ([installation guide](https://github.com/diffblue/cbmc))
- ESBMC ([installation guide](https://github.com/esbmc/esbmc))
- An LLM API key (to be specified in `.env`)

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

## Notes

- All student submissions in `data/submissions/` are anonymised before being added to the repository.
- The `data/` directory is excluded from version control via `.gitignore` to protect sensitive academic data.
