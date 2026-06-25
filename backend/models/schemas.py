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