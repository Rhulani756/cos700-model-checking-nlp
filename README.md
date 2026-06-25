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

## System Architecture

```
┌─────────────────────┐        HTTP        ┌──────────────────────┐
│  Frontend (Next.js) │  ─────────────────▶│  Backend (FastAPI)   │
│  localhost:3000     │◀─────────────────  │  localhost:8000      │
└─────────────────────┘                    └──────────┬───────────┘
                                                      │
                                                      ▼
                                           ┌──────────────────────┐
                                           │  Pipeline (Python)   │
                                           │  CBMC / ESBMC        │
                                           │  Parser              │
                                           │  LLM Client          │
                                           └──────────────────────┘
```

The frontend handles student interaction. The backend exposes a REST API and coordinates the pipeline. The pipeline runs model checking, parses counterexamples, and generates feedback via an LLM.

---

## Verification Properties

The system targets four classes of logical errors common in introductory programming:

- **Array bounds**: out-of-bounds array access
- **Null safety**: null pointer dereferences
- **Loop termination**: non-terminating or incorrectly bounded loops
- **Division by zero**: arithmetic errors under specific execution paths

---



## Repository Structure

```
cos700-model-checking-nlp/
│
├── frontend/                              # Next.js student interface
│   ├── src/app/
│   │   ├── page.tsx                       # Submission form
│   │   └── results/page.tsx              # Feedback display
│   ├── .env.local                         # NEXT_PUBLIC_API_URL (not committed)
│   └── README.md
│
├── backend/                               # FastAPI REST API
│   ├── main.py                            # Entry point, CORS, router registration
│   ├── routers/feedback.py                # /api/feedback endpoint
│   ├── models/schemas.py                  # Pydantic request/response models
│   ├── .env                               # API keys (not committed)
│   └── README.md
│
├── pipeline/                              # Core Python pipeline
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
└── README.md
```

---

## Setup

> Full setup instructions will be added in Milestone 2 once the environment is configured.

### Prerequisites

- Node.js 18+
- Python 3.10+
- CBMC ([installation guide](https://github.com/diffblue/cbmc))
- ESBMC ([installation guide](https://github.com/esbmc/esbmc))
- An LLM API key (Anthropic or Gemini)

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # then set NEXT_PUBLIC_API_URL
npm run dev                         # http://localhost:3000
```

See `frontend/README.md` for full details.

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env               # then set your API key
uvicorn main:app --reload --port 8000
```

See `backend/README.md` for full details.

### Pipeline (standalone)

```bash
pip install -r requirements.txt
```

### Health Check

With the backend running:

```bash
curl http://localhost:8000/health
# { "status": "ok" }
```

---

## Milestones

| # | Milestone | Description |
|---|---|---|
| 1 | Project Initialisation | Finalise proposal; study CBMC/ESBMC output for all four properties |
| 2 | Environment & Data | Install model checkers; gather and anonymise C/C++ submissions |
| 3 | Module Design | Develop the NLP translation layer mapping counterexamples to natural language |
| 4 | System Integration | Connect model checker pipeline to NLP module and backend API end-to-end |
| 5 | Evaluation | User study with students; collect quantitative and qualitative data |
| 6 | Final Reporting | Analyse results and write final research report |

---

## Branching Strategy

```
main
└── dev                          ← integration branch (all PRs merge here)
    ├── feat/pipeline-model-checker
    ├── feat/pipeline-parser
    ├── feat/pipeline-nlp
    ├── feat/pipeline-feedback
    ├── feat/backend-api
    └── feat/frontend-ui
```

### Branch Rules

| Branch | Purpose | Who merges |
|---|---|---|
| `main` | Stable, supervisor-presentable code | PR from `dev` only, requires 2 reviews |
| `dev` | Integration, all feature branches merge here first | PR from any `feat/*`, requires 1 review |
| `feat/*` | Individual feature development | Author opens PR into `dev` |

### Workflow

```bash
# Always branch from dev
git checkout dev && git pull
git checkout -b feat/pipeline-parser

# Commit often with descriptive messages
git commit -m "feat(parser): extract violation type and line number from CBMC output"

# Push and open a PR into dev
git push -u origin feat/pipeline-parser
```

### Commit Message Format

```
<type>(<scope>): <short description>

types:  feat | fix | chore | docs | refactor | test
scopes: parser | model-checker | nlp | feedback | backend | frontend
```

Examples:
```
feat(nlp): add one-shot prompt template for array bounds
fix(parser): handle ESBMC output format for null dereference
docs(backend): update README with health check endpoint
chore(frontend): scaffold Next.js app with Tailwind
```