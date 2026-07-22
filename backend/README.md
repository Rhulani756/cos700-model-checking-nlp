# Backend API

FastAPI backend that sits between the Next.js frontend and the Python pipeline. Accepts student C++ submissions, runs them through the model checker and NLP pipeline, and returns structured pedagogical feedback.

---

## Stack

| Tool | Purpose |
|---|---|
| FastAPI | API framework |
| Uvicorn | ASGI server |
| Pydantic | Request/response validation |
| python-dotenv | Environment variable management |

---

## Structure

```
backend/
├── main.py              # App entry point, CORS config, router registration
├── routers/
│   └── feedback.py      # /api/feedback endpoint
├── models/
│   └── schemas.py       # Pydantic request and response models
├── requirements.txt
└── README.md
```

---

## Endpoints

| Method | Route | Description |
|---|---|---|
| `GET` | `/health` | Health check — returns `{ "status": "ok" }` |
| `POST` | `/api/feedback` | Submit a C++ program and receive feedback |

### `POST /api/feedback`

**Request body:**

```json
{
  "source_code": "int main() { ... }",
  "filename": "submission.c",
  "tool": "cbmc",
  "feedback_type": "KM",
  "output_category": "natural_language",
  "prompt_type": "one_shot"
}
```

| Field | Type | Options | Default |
|---|---|---|---|
| `source_code` | string | — | required |
| `filename` | string | — | required |
| `tool` | string | `cbmc`, `esbmc` | `cbmc` |
| `feedback_type` | string | `KC`, `KM`, `KH`, `KMC` | `KM` |
| `output_category` | string | `natural_language`, `visual` | `natural_language` |
| `prompt_type` | string | `zero_shot`, `one_shot` | `one_shot` |

**Feedback type reference:**

| Code | Meaning |
|---|---|
| `KC` | Knowledge about concepts |
| `KM` | Knowledge about mistakes |
| `KH` | Knowledge on how to proceed |
| `KMC` | Knowledge about meta-cognition |

**Response body:**

```json
{
  "verification_status": "FAILED",
  "error_type": "array_bounds",
  "line": 15,
  "feedback": "Your program attempts to access...",
  "raw_output": "CBMC version 6.8.0..."
}
```

---

## Setup

### Prerequisites

- Python 3.10+
- CBMC or ESBMC installed and on `PATH`
- An LLM API key

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in this directory:

```
ANTHROPIC_API_KEY=sk-ant-...
# or
GEMINI_API_KEY=...
```

### Run the Development Server

```bash
uvicorn main:app --reload --port 8000
```

The API runs on [http://localhost:8000](http://localhost:8000).

### Interactive API Docs

FastAPI auto-generates documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Health Check

```bash
curl http://localhost:8000/health
# { "status": "ok" }
```

---

## Notes

- `.env` is excluded from version control, do not commit API keys.
- The backend imports from `pipeline/`; ensure the project root is on `PYTHONPATH` when running, or install the pipeline as a local package.
- CORS is configured to allow requests from `http://localhost:3000` (Next.js dev server) only. Update `allow_origins` in `main.py` before deploying to production.
- Full pipeline wiring is to be completed in Milestone 4 (System Integration).