from typing import List, Optional, Literal
from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    submission_id: str
    compilation_mode: Literal["independent", "combined"] = "independent"

class FileStatus(BaseModel):
    file: str
    verification_status: str  # "FAILED" | "SUCCESSFUL" | "UNKNOWN" | "ERROR"
    has_feedback_error: bool = False

class FeedbackResponse(BaseModel):
    file: str
    verification_status: str
    error_type: Optional[str] = None
    line: Optional[int] = None
    feedback: Optional[dict] = None       # PedagogicalFeedback, serialized
    diagram_svg: str = ""
    diagram_render_error: str = ""
    raw_output: str
    other_files: List[FileStatus] = []     