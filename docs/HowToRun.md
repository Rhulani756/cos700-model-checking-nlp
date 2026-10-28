# How to Run

## 1. Frontend

```bash
cd frontend
npm install
npm run dev
```

Check that it's running in your browser: [http://localhost:3000](http://localhost:3000)

---

## 2. Environment Variables

Save a `.env` file in the `backend/nlp` directory with the following content:

```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.1-flash-lite
GEMINI_API_KEY=

PLANTUML_SERVER_URL=https://www.plantuml.com/plantuml
```

> Fill in `GEMINI_API_KEY` with your own key.

---

## 3. Backend

Run all commands from the **project root directory**.

### Set up the virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r backend/requirements.txt
pip install -r pipeline/nlp/requirements.txt
```

### Test the pipeline

```bash
python -m pipeline.pipeline_test > output.txt
```

### Start the backend server

If the pipeline test runs successfully, continue with:

```bash
python -m uvicorn backend.main:app --reload
```

---
## 6. Troubleshooting

| Symptom | Possible cause | Suggested fix |
|---|---|---|
| Frontend fails to start | Missing Node.js dependencies | Run `npm install` from the `frontend` directory. |
| Backend fails to start | Virtual environment is inactive or dependencies are missing | Activate `.venv` and install the required Python dependencies. |
| Gemini requests fail | Missing or invalid API key | Check `GEMINI_API_KEY` in `backend/nlp/.env` and verify that the key is valid. |
| Pipeline test fails | Configuration, dependency, or pipeline error | Review `output.txt` for diagnostic information. |
| Port is already in use | Another process is using the required port | Stop the conflicting process or configure the application to use another available port. |
| PlantUML diagrams fail to generate | Network connectivity or PlantUML server issue | Check your internet connection and verify `PLANTUML_SERVER_URL`. |