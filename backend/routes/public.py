import uuid
from datetime import datetime, timezone
from fastapi import APIRouter

from database import db
from models.auth import UserRole
from models.process import PublicClientRegistration
from services.email import send_new_client_notification
from services.alerts import notify_new_client_registration


router = APIRouter(prefix="/public", tags=["Public"])


@router.post("/client-registration")
async def public_client_registration(data: PublicClientRegistration):
    """
    Endpoint público para registo de clientes - sem autenticação.
    
    Quando o cliente preenche o formulário:
    1. Cria utilizador (se não existir)
    2. Cria processo
    3. Notifica administradores
    4. Se "Já tem imóvel" preenchido, indicar para atribuir só intermediários
    """
    
    existing_user = await db.users.find_one({"email": data.email})
    
    if existing_user:
        user_id = existing_user["id"]
        user_name = existing_user["name"]
    else:
        user_id = str(uuid.uuid4())
        user_name = data.name
        now = datetime.now(timezone.utc).isoformat()
        
        user_doc = {
            "id": user_id,
            "email": data.email,
            "password": None,
            "name": data.name,
            "phone": data.phone,
            "role": UserRole.CLIENTE,
            "is_active": True,
            "onedrive_folder": data.name,
            "created_at": now
        }
        await db.users.insert_one(user_doc)
    
    first_status = await db.workflow_statuses.find_one({}, {"_id": 0}, sort=[("order", 1)])
    initial_status = first_status["name"] if first_status else "clientes_espera"
    
    process_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    # Verificar se já tem imóvel (para definir atribuição)
    real_estate_data = data.real_estate_data.model_dump() if data.real_estate_data else {}
    has_property = bool(real_estate_data.get("ja_tem_imovel") or real_estate_data.get("has_property"))
    
    # Verificar idade para campo idade_menos_35
    personal_data = data.personal_data.model_dump() if data.personal_data else {}
    birth_date = personal_data.get("birth_date")
    idade_menos_35 = False
    if birth_date:
        try:
            birth = datetime.strptime(birth_date, "%Y-%m-%d")
            age = (datetime.now() - birth).days // 365
            idade_menos_35 = age < 35
        except:
            pass
    
    process_doc = {
        "id": process_id,
        "client_id": user_id,
        "client_name": user_name,
        "client_email": data.email,
        "client_phone": data.phone,
        "process_type": data.process_type,
        "status": initial_status,
        "personal_data": personal_data,
        "titular2_data": data.titular2_data.model_dump() if data.titular2_data else None,
        "financial_data": data.financial_data.model_dump() if data.financial_data else None,
        "real_estate_data": real_estate_data,
        "credit_data": None,
        "assigned_consultor_id": None,
        "assigned_mediador_id": None,
        "consultor_id": None,
        "intermediario_id": None,
        "source": "public_form",
        "has_property": has_property,  # Flag para indicar se já tem imóvel
        "idade_menos_35": idade_menos_35,  # Flag para apoio ao estado
        "created_at": now,
        "updated_at": now
    }
    
    await db.processes.insert_one(process_doc)
    
    await db.history.insert_one({
        "id": str(uuid.uuid4()),
        "process_id": process_id,
        "user_id": user_id,
        "user_name": user_name,
        "action": "Cliente registou-se via formulário público",
        "field": None,
        "old_value": None,
        "new_value": None,
        "created_at": now
    })
    
    # Send notifications to staff
    staff = await db.users.find(
        {"role": {"$in": [UserRole.ADMIN, UserRole.CONSULTOR, UserRole.MEDIADOR]}}, 
        {"_id": 0}
    ).to_list(100)
    
    for member in staff:
        await send_new_client_notification(
            client_name=data.name,
            client_email=data.email,
            client_phone=data.phone,
            process_type=data.process_type,
            staff_email=member["email"],
            staff_name=member["name"]
        )
    
    return {
        "success": True,
        "message": "Registo criado com sucesso",
        "process_id": process_id
    }
