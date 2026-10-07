from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import feedback, upload, files
import shutil

app = FastAPI(title="COS700 Feedback API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "tauri://localhost" , "https://tauri.localhost","http://127.0.0.1:1430",
        "http://localhost:1430",],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(feedback.router, prefix="/api")
app.include_router(upload.router, prefix="/api")
app.include_router(files.router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/esbmc")
async def check_esbmc():
    path = shutil.which("esbmc")
    if not path:
        return {"installed": False}
    return {"installed": True, "path": path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)