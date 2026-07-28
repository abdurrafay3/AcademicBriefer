from pydantic import BaseModel, Field
from typing import Literal,Optional
from datetime import datetime

class CanvasItem(BaseModel):
    course_id: str = Field(..., description="Unique identifier for the course.")
    source : Literal["assignment", "quiz", "exam", "announcement"] = Field(..., description="Source of the item in Canvas.")
    title: str = Field(..., description="Title of the Canvas item.")
    due_at: Optional[datetime] = Field(None, description="Due date and time for the Canvas item, if applicable.")
    body_text: Optional[str] = Field(None, description="Plain text content of the Canvas item, if applicable.")
    trust_due_date : bool = Field(..., description="Whether to trust the due date for the Canvas item.")

class CanvasScraperResult(BaseModel):
    items: list[CanvasItem] = Field(..., description="List of items scraped from Canvas.")
    scrape_status : Literal["success", "failure", "partial", "login_failed"] = Field(..., description="Status of the Canvas scraping operation.")
    scraped_at: str = Field(..., description="Timestamp when the Canvas scraping operation was performed.")


