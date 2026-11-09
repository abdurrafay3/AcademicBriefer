from typing import Literal

from pydantic import BaseModel, Field

from backend.schemas.email import EmailDigest
from backend.services.courses.canvas_scraper import Assignment


class BriefingResponse(BaseModel):
    generated_at: str = Field(..., description="Timestamp when the briefing was generated.")
    email_status: Literal["success", "failed"] = Field(..., description="Status of the email scraping step.")
    canvas_status: Literal["success", "failed"] = Field(..., description="Status of the Canvas scraping step.")
    calendar_status: Literal["success", "failed", "skipped"] = Field(
        ..., description="Status of syncing Canvas assignments to the calendar."
    )
    emails_scraped: int = Field(..., description="Number of emails fetched.")
    assignments: list[Assignment] = Field(default_factory=list, description="Canvas assignments scraped.")
    summary: EmailDigest | None = Field(None, description="LLM-generated summary of emails and Canvas assignments.")
