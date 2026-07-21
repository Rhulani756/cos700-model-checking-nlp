import shutil
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

router = APIRouter()

ALLOWED_EXTENSIONS = {".cpp", ".h"}
MAX_FILE_SIZE = 5 * 1024 * 1024      # 5 MB per file
MAX_TOTAL_SIZE = 50 * 1024 * 1024    # 50 MB per submission

SUBMISSIONS_ROOT = (Path(__file__).resolve().parent / ".." / ".." / "data" / "student_submissions").resolve()
SUBMISSIONS_ROOT.mkdir(parents=True, exist_ok=True)


class UploadResponse(BaseModel):
    submission_id: str
    files: List[str]


def _sanitize_path(relative_path: str) -> Path:
    cleaned = relative_path.replace("\\", "/").lstrip("/")
    path = Path(cleaned)
    if not path.parts or any(part in ("..", "") for part in path.parts):
        raise HTTPException(status_code=400, detail=f"Invalid path: {relative_path!r}")
    return path


@router.post("/upload", response_model=UploadResponse)
async def upload_submission(
    files: List[UploadFile] = File(...),
    relative_paths: List[str] = Form(...),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided.")

    if len(files) != len(relative_paths):
        raise HTTPException(
            status_code=400,
            detail="files and relative_paths must be the same length.",
        )

    submission_id = uuid.uuid4().hex
    submission_dir = SUBMISSIONS_ROOT / submission_id
    submission_dir.mkdir(parents=True, exist_ok=False)

    saved_files: List[str] = []
    total_size = 0

    try:
        for upload_file, rel_path in zip(files, relative_paths):
            ext = Path(upload_file.filename or "").suffix.lower()
            if ext not in ALLOWED_EXTENSIONS:
                continue 

            safe_rel_path = _sanitize_path(rel_path or upload_file.filename)
            dest_path = submission_dir / safe_rel_path

            if submission_dir not in dest_path.resolve().parents:
                raise HTTPException(status_code=400, detail="Invalid destination path.")

            dest_path.parent.mkdir(parents=True, exist_ok=True)

            size = 0
            with open(dest_path, "wb") as out_file:
                while chunk := await upload_file.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_FILE_SIZE:
                        raise HTTPException(
                            status_code=413,
                            detail=f"{upload_file.filename} exceeds the {MAX_FILE_SIZE} byte limit.",
                        )
                    out_file.write(chunk)

            total_size += size
            if total_size > MAX_TOTAL_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="Submission exceeds the total size limit.",
                )

            saved_files.append(str(safe_rel_path))
            await upload_file.close()

        if not saved_files:
            raise HTTPException(
                status_code=400,
                detail="No .cpp or .h files found in the upload.",
            )

    except HTTPException:
        shutil.rmtree(submission_dir, ignore_errors=True)
        raise
    except Exception as exc:
        shutil.rmtree(submission_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {exc}") from exc

    return UploadResponse(submission_id=submission_id, files=saved_files)