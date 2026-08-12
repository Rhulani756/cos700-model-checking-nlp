from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.models.schemas import FeedbackRequest, FeedbackResponse
from pipeline.main import run_pipeline

router = APIRouter()

SUBMISSIONS_ROOT = (Path(__file__).resolve().parent / ".." / ".." / "data" / "student_submissions").resolve()

# backend/routers/feedback.py
@router.post("/feedback", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest):
    submission_dir = SUBMISSIONS_ROOT / request.submission_id

    if not submission_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Submission '{request.submission_id}' not found.")

    try:
        pipeline_result = await run_pipeline(submission_dir, mode=request.compilation_mode)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    entries = pipeline_result["results"]
    if not entries:
        raise HTTPException(status_code=500, detail="Pipeline produced no results.")

    chosen = next(
        (e for e in entries if e.get("verification_result") == "FAILED" and "feedback_error" not in e),
        entries[0],
    )
    other_files = [e["file"] for e in entries if e is not chosen]

    counterexample = chosen.get("counterexample") or {}
    diagram = chosen.get("diagram") or {}

    return FeedbackResponse(
        file=chosen["file"],
        verification_status=chosen["verification_result"],
        error_type=counterexample.get("violation_type"),
        line=counterexample.get("line"),
        feedback=chosen.get("feedback"),
        diagram_svg=diagram.get("svg", ""),
        diagram_render_error=diagram.get("render_error", ""),
        raw_output=chosen["raw_output"],
        other_files=other_files,
    )


# @router.post("/feedback", response_model=FeedbackResponse)
# async def generate_feedback(request: FeedbackRequest):
#     submission_dir = SUBMISSIONS_ROOT / request.submission_id

#     if not submission_dir.is_dir():
#         raise HTTPException(status_code=404, detail=f"Submission '{request.submission_id}' not found.")

#     try:
#         pipeline_result = await run_pipeline(submission_dir)
#     except FileNotFoundError as e:
#         raise HTTPException(status_code=404, detail=str(e))
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

#     entries = pipeline_result["results"]
#     if not entries:
#         raise HTTPException(status_code=500, detail="Pipeline produced no results.")

#     # Prefer the first file that failed verification; fall back to the first file overall.
#     chosen = next((e for e in entries if e.get("verification_result") == "FAILED"), entries[0])
#     other_files = [e["file"] for e in entries if e is not chosen]

#     counterexample = chosen.get("counterexample") or {}
#     diagram = chosen.get("diagram") or {}

#     return FeedbackResponse(
#         file=chosen["file"],
#         verification_status=chosen["verification_result"],
#         error_type=counterexample.get("violation_type"),
#         line=counterexample.get("line"),
#         feedback=chosen.get("feedback"),
#         diagram_svg=diagram.get("svg", ""),
#         diagram_render_error=diagram.get("render_error", ""),
#         raw_output=chosen["raw_output"],
#         other_files=other_files,
#     )