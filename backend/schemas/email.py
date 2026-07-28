from pydantic import BaseModel, Field
from backend.schemas.deadline import Deadline, Opportunity, Event


class NotLoggedInException(Exception):
    """Exception raised when the user is not logged in to their email account."""
    pass

class Email(BaseModel):
    subject: str = Field(..., description="The subject of the email")
    sender: str = Field(..., description="The sender of the email")
    timestamp: str = Field(..., description="The timestamp of the email")
    body: str = Field(..., description="The body of the email")

class EmailDigest(BaseModel):
    deadlines: list[Deadline]   
    opportunities: list[Opportunity]
    events: list[Event]
    important_announcements: list[str]