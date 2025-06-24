from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class Task(BaseModel):
    title: str
    description: str
    status: str
    start_date: date
    end_date: date
    assigned_to: str

class Project(BaseModel):
    name: str
    description: str
    status: str
    progress: int = Field(ge=0, le=100)
    team: List[str]
    dueDate: date
    priority: str
