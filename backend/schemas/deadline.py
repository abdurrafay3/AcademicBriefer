from typing import Literal
from pydantic import BaseModel, Field

class Deadline(BaseModel):
    title: str = Field(..., description="The title of the deadline")
    due_date: str = Field(..., description="The due date of the deadline")
    description: str = Field(..., description="A brief description of the deadline")
    priority : Literal["HIGH", "MEDIUM", "LOW"] = Field(..., description="The priority level of the deadline")

class Opportunity(BaseModel):
    title: str = Field(..., description="The title of the opportunity")
    deadline: str | None = Field(None, description="The deadline for the opportunity, if applicable")
    description: str = Field(..., description="A brief description of the opportunity")

class Event(BaseModel):
    title: str = Field(..., description="The title of the event")
    date: str = Field(..., description="The date of the event")
    location: str | None = Field(None, description="The location of the event")