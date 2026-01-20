from pydantic import BaseModel
from typing import Optional


class DeadlineCreate(BaseModel):
    process_id: Optional[str] = None  # Optional - can create general deadline
    title: str
    description: Optional[str] = None
    due_date: str
    priority: str = "medium"
    assigned_consultor_id: Optional[str] = None
    assigned_mediador_id: Optional[str] = None


class DeadlineUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    completed: Optional[bool] = None
    assigned_consultor_id: Optional[str] = None
    assigned_mediador_id: Optional[str] = None


class DeadlineResponse(BaseModel):
    id: str
    process_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    due_date: str
    priority: str
    completed: bool
    created_by: str
    created_at: str
    assigned_consultor_id: Optional[str] = None
    assigned_mediador_id: Optional[str] = None
