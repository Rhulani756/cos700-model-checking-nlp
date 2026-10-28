<div align="center">

# Model Checking × NLP
### Pedagogic feedback on programming assignments

*Turning ESBMC counterexamples into explanations novice programmers can actually use.*

![COS700](https://img.shields.io/badge/COS700-Honours_Research-1f3a8a?style=flat-square)
![C++](https://img.shields.io/badge/target-C%2B%2B-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![ESBMC](https://img.shields.io/badge/verifier-ESBMC-b45309?style=flat-square)
![Gemini](https://img.shields.io/badge/LLM-Gemini_3.1_Flash--Lite-4285F4?style=flat-square&logo=googlegemini&logoColor=white)
![Next.js](https://img.shields.io/badge/frontend-Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)

[Overview](#overview) · [Pipeline](#pipeline) · [Quick start](#quick-start) · [Results](#results) · [Limitations](#limitations) · [Team](#team)

</div>

---

## Overview

Most automated graders say *that* a program fails, not *why*. Bounded model checkers can find the real logical errors, but their counterexample traces are long, repetitive and unreadable to beginners.

This project bridges the gap. **ESBMC proves the violation; the LLM only explains it.** Every explanation is grounded in a verified counterexample, so the feedback is tied to evidence rather than the model's guess.

Each piece of feedback gives:

| Element | Purpose |
|---|---|
| 🔎 **What** went wrong | the violated property and where |
| 🧠 **Why** it went wrong | the root cause, in plain language |
| 🛠 **What** to change | concrete, non-complete guidance |
| ❓ **A question** | prompts the student to reason about the fix |
| 🗺 **A diagram** | the execution path leading to the error |

**Properties checked:** array bounds · null-pointer dereference · division by zero · loop termination (unwinding assertion, bound 50)

## Pipeline

```
Student C++ submission
        │
        ▼
ESBMC model checking ── raw trace ──▶ Parser
                                        │ structured counterexample
                                        ▼
                                  NLP module (Gemini)
                                   │             │
                                   ▼             ▼
                            Text feedback   Execution-path diagram
```

<details>
<summary><b>Stage details</b></summary>

1. **Model checking**: two parallel ESBMC runs. A trace run (`--unwind`, `--compact-trace`) captures the first counterexample; an overview run (`--multi-property`, `--result-only`) marks each property *passed*, *failed* or *undetermined*. 60 s timeout.
2. **Parser**: extracts violation location, type, condition and the variable assignments leading to the error.
3. **NLP module**: property-specific prompt → Gemini 3.1 Flash-Lite (temperature 0.2, 1400 max tokens) → Pydantic schema validation. Two attempts, then a deterministic fallback.
4. **Graph generator**: builds PlantUML / SVG from the trace plus optional LLM step annotations.

</details>

## Repository

```
├── frontend/     Next.js student interface
├── backend/      FastAPI REST API
├── pipeline/     model checker runner · parser · NLP module · formatter
├── data/         anonymised submissions and raw checker output
├── evaluation/   questionnaire, results, scripts
└── reports/      COS700 research report
```

## Quick start

**Prerequisites:** Node.js 18+ · Python 3.10+ · [ESBMC](https://github.com/esbmc/esbmc) on your `PATH` · a Gemini API key

<table>
<tr>
<td width="50%" valign="top">

**Backend** · `localhost:8000`
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # add API key
uvicorn main:app --reload --port 8000
```

</td>
<td width="50%" valign="top">

**Frontend** · `localhost:3000`
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

</td>
</tr>
</table>

Health check: `curl http://localhost:8000/health` → `{"status": "ok"}`

## Results

Within-subject survey · **13 participants** · **8 programs** · seven 5-point Likert items per feedback item.

| Feedback condition | "Strongly agree" | Neutral / negative |
|---|---:|---:|
| Raw ESBMC output | 5.4%* | 80.3% |
| LLM only (ungrounded) | 63.7% | 6.6% |
| **Integrated, text** | **93.4%** | **0%** |
| Integrated, diagram only | 49.5% | 20.9% |
| **Integrated, text + diagram** | **90.1%** | **1.1%** |

<sub>*Not stated in the report; derived as 100 − 80.3 − 14.3 (agree) from Figure 4. Neutral/negative = 18.7 + 33.0 + 28.6.</sub>

- 🥇 **11 of 13** chose text + diagram as most helpful.
- 🥉 **12 of 13** named raw ESBMC output least helpful.
- Diagram-only was weakest on *"clear ideas on how to proceed"*.

> These are perceived-usefulness results from a small study. They do not measure learning gains or feedback accuracy.

## Limitations

- Single-file C++ programs, four properties, one counterexample explained per run
- Loop check is a bound check, **not** a general termination analysis
- One LLM, one prompt; suggested changes and example fixes can reveal the solution
- Small single-institution sample with a fixed presentation order

## Team

<div align="center">

| Simphiwe Jessica Zitha | Lwando Msindo | Rhulani Matiane | Kagiso Mosehla |
|:---:|:---:|:---:|:---:|

**Supervisor:** Prof. Nils Timm  
Department of Computer Science, University of Pretoria · October 2026

</div>

## Contributing

Branches: `main` · `dev` · `feat/*`  
Commits: `<type>(<scope>): <description>`

---

<div align="center"><sub>COS700 Honours Research Project · University of Pretoria</sub></div>
