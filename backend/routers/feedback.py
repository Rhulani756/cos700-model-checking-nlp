from pathlib import Path
from typing import Any, Dict
import asyncio
import json
from fastapi import APIRouter, HTTPException
from backend.models.schemas import FeedbackRequest, FeedbackResponse, FileStatus
from pipeline.main import run_pipeline
from fastapi.responses import StreamingResponse

router = APIRouter()

SUBMISSIONS_ROOT = (Path(__file__).resolve().parent / ".." / ".." / "data" / "student_submissions").resolve()

def _flatten_result(pipeline_result: Dict[str, Any]) -> FeedbackResponse:
    """Pick one result to surface to the frontend and normalize the shape.

    Prefers the first file that failed verification and generated feedback
    successfully. Falls back to the first entry overall (e.g. all files
    passed, or every failing file also hit a feedback_error).
    """
    entries = pipeline_result["results"]
    if not entries:
        raise ValueError("Pipeline produced no results.")

    chosen = next(
        (e for e in entries if e.get("verification_result") == "FAILED" and "feedback_error" not in e),
        entries[0],
    )

    other_files = [
        FileStatus(
            file=e["file"],
            verification_status=e.get("verification_result", "ERROR"),
            has_feedback_error="feedback_error" in e,
        )
        for e in entries
        if e is not chosen
    ]

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
        passed_properties=chosen.get("passed_properties", []),
        failed_properties=chosen.get("failed_properties", []),
        undetermined_properties=chosen.get("undetermined_properties", []),
    )


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

    try:
        return _flatten_result(pipeline_result)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/stream")
async def generate_feedback_stream(request: FeedbackRequest):
    submission_dir = SUBMISSIONS_ROOT / request.submission_id
    if not submission_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Submission '{request.submission_id}' not found.")

    async def event_generator():
        queue: asyncio.Queue = asyncio.Queue()

        def on_stage(stage: str, detail: str = ""):
            queue.put_nowait({"type": "stage", "stage": stage, "detail": detail})

        async def run():
            try:
                pipeline_result = await run_pipeline(
                    submission_dir, mode=request.compilation_mode, on_stage=on_stage
                )
                flattened = _flatten_result(pipeline_result)
                await queue.put({"type": "result", "data": flattened.model_dump()})
            except Exception as e:
                await queue.put({"type": "error", "detail": str(e)})
            finally:
                await queue.put(None)  # sentinel: stream done

        task = asyncio.create_task(run())

        while True:
            item = await queue.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

        await task

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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