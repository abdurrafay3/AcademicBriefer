import logging

from fastapi import APIRouter, HTTPException

from backend.schemas.briefing import BriefingResponse
from backend.services.briefing.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/briefing", tags=["briefing"])


@router.post("/generate", response_model=BriefingResponse)
def generate_briefing() -> BriefingResponse:
    """Fetches emails, scrapes Canvas, syncs assignments to the calendar, and
    generates an LLM summary of what matters from both sources."""
    try:
        return Orchestrator().orchestrate()
    except Exception as e:
        logger.exception("Briefing generation failed")
        raise HTTPException(status_code=500, detail=str(e)) from e
