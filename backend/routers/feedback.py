from fastapi import APIRouter
from models.schemas import FeedbackRequest, FeedbackResponse

router = APIRouter()

@router.post("/feedback", response_model=FeedbackResponse)
async def generate_feedback(request: FeedbackRequest):
    # Will wire to pipeline in Milestone 4
    pass