<<<<<<< HEAD
from pydantic import BaseModel
from typing import Literal

class FeedbackRequest(BaseModel):
    source_code: str
    filename: str
    tool: Literal["cbmc", "esbmc"] = "cbmc"
    feedback_type: Literal["KC", "KM", "KH", "KMC"] = "KM"
    output_category: Literal["natural_language", "visual"] = "natural_language"
    prompt_type: Literal["zero_shot", "one_shot"] = "one_shot"

class FeedbackResponse(BaseModel):
    verification_status: str
    error_type: str | None
    line: int | None
    feedback: str
    raw_output: str
=======
from typing import List, Optional, Literal
from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    submission_id: str
    compilation_mode: Literal["independent", "combined"] = "independent"

class FeedbackResponse(BaseModel):
    file: str
    verification_status: str
    error_type: Optional[str] = None
    line: Optional[int] = None
    feedback: Optional[dict] = None       # PedagogicalFeedback, serialized
    diagram_svg: str = ""
    diagram_render_error: str = ""
    raw_output: str
    other_files: List[str] = []           # names of any other files in the submission, unprocessed for feedback
>>>>>>> origin/feature/ui+pipeline
