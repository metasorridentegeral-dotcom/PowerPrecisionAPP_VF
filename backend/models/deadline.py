from pydantic import BaseModel
from typing import Optional


class DeadlineCreate(BaseModel):
    process_id: str
    title: str
    description: Optional[str] = None
    due_date: str
    priority: str = "medium"


class DeadlineUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None


class DeadlineResponse(BaseModel):
    id: str
    process_id: str
    title: str
    description: Optional[str] = None
    due_date: str
    priority: str
    completed: bool
    created_by: str
    created_at: str
