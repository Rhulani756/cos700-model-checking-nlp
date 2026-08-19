<<<<<<< HEAD
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import feedback

app = FastAPI(title="COS700 Feedback API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router, prefix="/api")

@app.get("/health")
async def health_check():
=======
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import feedback, upload

app = FastAPI(title="COS700 Feedback API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

@app.get("/health")
async def health_check():
>>>>>>> origin/feature/ui+pipeline
    return {"status": "ok"}