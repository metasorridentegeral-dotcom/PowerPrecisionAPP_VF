from pydantic import BaseModel
from typing import Optional


class DocumentExpiry(BaseModel):
    """Document expiry date tracking for a client."""
    process_id: str
    document_type: str  # 'cc', 'carta_conducao', 'passaporte', 'contrato_trabalho', etc.
    document_name: str
    expiry_date: str  # YYYY-MM-DD
    notes: Optional[str] = None


class DocumentExpiryCreate(BaseModel):
    process_id: str
    document_type: str
    document_name: str
    expiry_date: str
    notes: Optional[str] = None


class DocumentExpiryUpdate(BaseModel):
    document_name: Optional[str] = None
    expiry_date: Optional[str] = None
    notes: Optional[str] = None


class DocumentExpiryResponse(BaseModel):
    id: str
    process_id: str
    document_type: str
    document_name: str
    expiry_date: str
    notes: Optional[str] = None
    created_at: str
    created_by: str
