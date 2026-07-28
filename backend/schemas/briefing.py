from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from deadline import Deadline


# this will be the output of the orchestrator agent
class Briefing(BaseModel): 
    generated_at: str = Field(..., description="Timestamp when the briefing was generated.")
    deadlines_added : list[Deadline]
    deadlines_needing_review : list[Deadline] = Field(..., description="List of deadlines that require review or confirmation.")
    email_status: Literal["success", "failure", "partial", "login_failed"] = Field(..., description="Status of the email scraping operation.")
    canvas_status: Literal["success", "failure", "partial", "login_failed"] = Field(..., description="Status of the Canvas scraping operation.")


