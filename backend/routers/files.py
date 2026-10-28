from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

from backend.paths import SUBMISSIONS_ROOT
# SUBMISSIONS_ROOT = (Path(__file__).resolve().parent / ".." / ".." / "data" / "student_submissions").resolve()

ALLOWED_EXTENSIONS = {".cpp", ".h"}
MAX_FILE_READ_SIZE = 3 * 1024 * 1024  # 2 MB — plenty for a source file, guards against surprises


class FileInfo(BaseModel):
    path: str
    size: int


class FileListResponse(BaseModel):
    submission_id: str
    files: List[FileInfo]


class FileContentResponse(BaseModel):
    path: str
    content: str


def _resolve_submission_dir(submission_id: str) -> Path:
    submission_dir = SUBMISSIONS_ROOT / submission_id
    if not submission_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Submission '{submission_id}' not found.")
    return submission_dir


def _safe_resolve_file(submission_dir: Path, relative_path: str) -> Path:
    """Reject paths that don't stay inside submission_dir."""
    cleaned = relative_path.replace("\\", "/").lstrip("/")
    candidate = (submission_dir / cleaned).resolve()

    if submission_dir not in candidate.parents and candidate != submission_dir:
        raise HTTPException(status_code=400, detail="Invalid file path.")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail=f"File '{relative_path}' not found in submission.")
    if candidate.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type '{candidate.suffix}' is not previewable.")

    return candidate


@router.get("/files/{submission_id}", response_model=FileListResponse)
async def list_submission_files(submission_id: str):
    """List every previewable file in a submission, with sizes."""
    submission_dir = _resolve_submission_dir(submission_id)

    files = [
        FileInfo(
            path=str(p.relative_to(submission_dir)),
            size=p.stat().st_size,
        )
        for p in sorted(submission_dir.rglob("*"))
        if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS
    ]

    return FileListResponse(submission_id=submission_id, files=files)


@router.get("/files/{submission_id}/content", response_model=FileContentResponse)
async def get_submission_file(submission_id: str, path: str):
    """Return the text content of one file within a submission, for preview."""
    submission_dir = _resolve_submission_dir(submission_id)
    file_path = _safe_resolve_file(submission_dir, path)

    if file_path.stat().st_size > MAX_FILE_READ_SIZE:
        raise HTTPException(status_code=413, detail="File is too large to preview.")

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not read file: {exc}")

    return FileContentResponse(path=path, content=content)

# file editing
class FileWriteRequest(BaseModel):
    content: str


class FileWriteResponse(BaseModel):
    path: str
    size: int


@router.put("/files/{submission_id}/content", response_model=FileWriteResponse)
async def save_submission_file(submission_id: str, path: str, request: FileWriteRequest):
    """Overwrite one file's content within a submission."""
    submission_dir = _resolve_submission_dir(submission_id)
    file_path = _safe_resolve_file(submission_dir, path)

    if len(request.content.encode("utf-8")) > MAX_FILE_READ_SIZE:
        raise HTTPException(status_code=413, detail="File content is too large.")

    try:
        file_path.write_text(request.content, encoding="utf-8")
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"Could not write file: {exc}")

    return FileWriteResponse(path=path, size=file_path.stat().st_size)