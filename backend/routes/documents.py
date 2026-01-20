"""
Document Expiry Management Routes
Track and manage document expiry dates for clients
"""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from database import db
from models.auth import UserRole
from models.document import DocumentExpiryCreate, DocumentExpiryUpdate, DocumentExpiryResponse
from services.auth import get_current_user, require_roles


router = APIRouter(prefix="/documents", tags=["Document Management"])


@router.post("/expiry", response_model=DocumentExpiryResponse)
async def create_document_expiry(
    data: DocumentExpiryCreate,
    user: dict = Depends(require_roles([UserRole.ADMIN, UserRole.CONSULTOR, UserRole.MEDIADOR]))
):
    """Create a new document expiry record for a process."""
    # Verify process exists
    process = await db.processes.find_one({"id": data.process_id})
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    doc = {
        "id": doc_id,
        "process_id": data.process_id,
        "document_type": data.document_type,
        "document_name": data.document_name,
        "expiry_date": data.expiry_date,
        "notes": data.notes,
        "created_at": now,
        "created_by": user["id"]
    }
    
    await db.document_expiries.insert_one(doc)
    
    return DocumentExpiryResponse(**{k: v for k, v in doc.items() if k != "_id"})


@router.get("/expiry", response_model=List[DocumentExpiryResponse])
async def get_document_expiries(
    process_id: Optional[str] = None,
    user: dict = Depends(get_current_user)
):
    """Get document expiries. Filter by process_id optionally."""
    query = {}
    
    if process_id:
        query["process_id"] = process_id
    elif user["role"] == UserRole.CONSULTOR:
        # Get processes assigned to this consultor
        processes = await db.processes.find(
            {"assigned_consultor_id": user["id"]}, 
            {"id": 1, "_id": 0}
        ).to_list(1000)
        process_ids = [p["id"] for p in processes]
        query["process_id"] = {"$in": process_ids}
    elif user["role"] == UserRole.MEDIADOR:
        # Get processes assigned to this mediador
        processes = await db.processes.find(
            {"assigned_mediador_id": user["id"]}, 
            {"id": 1, "_id": 0}
        ).to_list(1000)
        process_ids = [p["id"] for p in processes]
        query["process_id"] = {"$in": process_ids}
    
    docs = await db.document_expiries.find(query, {"_id": 0}).to_list(1000)
    return [DocumentExpiryResponse(**d) for d in docs]


@router.get("/expiry/upcoming")
async def get_upcoming_expiries(
    days: int = 30,
    user: dict = Depends(get_current_user)
):
    """Get documents expiring in the next N days."""
    from datetime import timedelta
    
    today = datetime.now(timezone.utc).date()
    future_date = today + timedelta(days=days)
    
    query = {
        "expiry_date": {
            "$gte": today.isoformat(),
            "$lte": future_date.isoformat()
        }
    }
    
    # Filter by user role
    if user["role"] == UserRole.CONSULTOR:
        processes = await db.processes.find(
            {"assigned_consultor_id": user["id"]}, 
            {"id": 1, "_id": 0}
        ).to_list(1000)
        process_ids = [p["id"] for p in processes]
        query["process_id"] = {"$in": process_ids}
    elif user["role"] == UserRole.MEDIADOR:
        processes = await db.processes.find(
            {"assigned_mediador_id": user["id"]}, 
            {"id": 1, "_id": 0}
        ).to_list(1000)
        process_ids = [p["id"] for p in processes]
        query["process_id"] = {"$in": process_ids}
    
    docs = await db.document_expiries.find(query, {"_id": 0}).sort("expiry_date", 1).to_list(1000)
    
    # Enrich with process info
    result = []
    for doc in docs:
        process = await db.processes.find_one({"id": doc["process_id"]}, {"_id": 0})
        if process:
            result.append({
                **doc,
                "client_name": process.get("client_name"),
                "client_email": process.get("client_email"),
                "process_status": process.get("status")
            })
    
    return result


@router.put("/expiry/{doc_id}", response_model=DocumentExpiryResponse)
async def update_document_expiry(
    doc_id: str,
    data: DocumentExpiryUpdate,
    user: dict = Depends(require_roles([UserRole.ADMIN, UserRole.CONSULTOR, UserRole.MEDIADOR]))
):
    """Update a document expiry record."""
    doc = await db.document_expiries.find_one({"id": doc_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Registo não encontrado")
    
    update_data = {}
    if data.document_name is not None:
        update_data["document_name"] = data.document_name
    if data.expiry_date is not None:
        update_data["expiry_date"] = data.expiry_date
    if data.notes is not None:
        update_data["notes"] = data.notes
    
    if update_data:
        await db.document_expiries.update_one({"id": doc_id}, {"$set": update_data})
    
    updated = await db.document_expiries.find_one({"id": doc_id}, {"_id": 0})
    return DocumentExpiryResponse(**updated)


@router.delete("/expiry/{doc_id}")
async def delete_document_expiry(
    doc_id: str,
    user: dict = Depends(require_roles([UserRole.ADMIN, UserRole.CONSULTOR, UserRole.MEDIADOR]))
):
    """Delete a document expiry record."""
    result = await db.document_expiries.delete_one({"id": doc_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Registo não encontrado")
    return {"message": "Registo eliminado"}


# Document type constants
DOCUMENT_TYPES = [
    {"type": "cc", "name": "Cartão de Cidadão", "icon": "id-card"},
    {"type": "passaporte", "name": "Passaporte", "icon": "passport"},
    {"type": "carta_conducao", "name": "Carta de Condução", "icon": "car"},
    {"type": "contrato_trabalho", "name": "Contrato de Trabalho", "icon": "file-text"},
    {"type": "declaracao_irs", "name": "Declaração de IRS", "icon": "file-text"},
    {"type": "comprovativo_morada", "name": "Comprovativo de Morada", "icon": "home"},
    {"type": "outro", "name": "Outro", "icon": "file"},
]


@router.get("/types")
async def get_document_types(user: dict = Depends(get_current_user)):
    """Get list of document types."""
    return DOCUMENT_TYPES
