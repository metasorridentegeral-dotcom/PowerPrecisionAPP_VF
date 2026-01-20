from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Config
JWT_SECRET = os.environ.get('JWT_SECRET', 'super-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== MODELS ==============

class UserRole:
    CLIENTE = "cliente"
    CONSULTOR = "consultor"
    MEDIADOR = "mediador"
    ADMIN = "admin"

class ProcessStatus:
    PEDIDO_INICIAL = "pedido_inicial"
    EM_ANALISE = "em_analise"
    AUTORIZACAO_BANCARIA = "autorizacao_bancaria"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"

class ProcessType:
    CREDITO = "credito"
    IMOBILIARIA = "imobiliaria"
    AMBOS = "ambos"

# Auth Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    role: str
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Process Models
class PersonalData(BaseModel):
    nif: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[str] = None
    marital_status: Optional[str] = None
    nationality: Optional[str] = None

class FinancialData(BaseModel):
    monthly_income: Optional[float] = None
    other_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_type: Optional[str] = None
    employer_name: Optional[str] = None
    employment_duration: Optional[str] = None
    has_debts: Optional[bool] = None
    debt_amount: Optional[float] = None

class RealEstateData(BaseModel):
    property_type: Optional[str] = None
    property_zone: Optional[str] = None
    desired_area: Optional[float] = None
    max_budget: Optional[float] = None
    property_purpose: Optional[str] = None
    notes: Optional[str] = None

class CreditData(BaseModel):
    requested_amount: Optional[float] = None
    loan_term_years: Optional[int] = None
    interest_rate: Optional[float] = None
    monthly_payment: Optional[float] = None
    bank_name: Optional[str] = None
    bank_approval_date: Optional[str] = None
    bank_approval_notes: Optional[str] = None

class ProcessCreate(BaseModel):
    process_type: str
    personal_data: Optional[PersonalData] = None
    financial_data: Optional[FinancialData] = None

class ProcessUpdate(BaseModel):
    personal_data: Optional[PersonalData] = None
    financial_data: Optional[FinancialData] = None
    real_estate_data: Optional[RealEstateData] = None
    credit_data: Optional[CreditData] = None
    status: Optional[str] = None

class ProcessResponse(BaseModel):
    id: str
    client_id: str
    client_name: str
    client_email: str
    process_type: str
    status: str
    personal_data: Optional[dict] = None
    financial_data: Optional[dict] = None
    real_estate_data: Optional[dict] = None
    credit_data: Optional[dict] = None
    assigned_consultor_id: Optional[str] = None
    assigned_mediador_id: Optional[str] = None
    created_at: str
    updated_at: str

# Deadline Models
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

# User Management Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    role: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

# ============== AUTH HELPERS ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="Utilizador não encontrado")
        if not user.get("is_active", True):
            raise HTTPException(status_code=401, detail="Conta desativada")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

def require_roles(allowed_roles: List[str]):
    async def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Permissão negada")
        return user
    return role_checker

# ============== EMAIL SERVICE (MOCK) ==============

async def send_email_notification(to_email: str, subject: str, body: str):
    """Mock email service - logs instead of sending"""
    logger.info(f"📧 EMAIL NOTIFICATION")
    logger.info(f"   To: {to_email}")
    logger.info(f"   Subject: {subject}")
    logger.info(f"   Body: {body[:100]}...")
    # Save to database for tracking
    await db.email_logs.insert_one({
        "id": str(uuid.uuid4()),
        "to": to_email,
        "subject": subject,
        "body": body,
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "status": "simulated"
    })
    return True

# ============== AUTH ROUTES ==============

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(data: UserRegister):
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email já registado")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": data.email,
        "password": hash_password(data.password),
        "name": data.name,
        "phone": data.phone,
        "role": UserRole.CLIENTE,
        "is_active": True,
        "created_at": now
    }
    
    await db.users.insert_one(user_doc)
    token = create_token(user_id, data.email, UserRole.CLIENTE)
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=data.email,
            name=data.name,
            phone=data.phone,
            role=UserRole.CLIENTE,
            created_at=now
        )
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email}, {"_id": 0})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="Conta desativada")
    
    token = create_token(user["id"], user["email"], user["role"])
    
    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            phone=user.get("phone"),
            role=user["role"],
            created_at=user["created_at"]
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        phone=user.get("phone"),
        role=user["role"],
        created_at=user["created_at"]
    )

# ============== PROCESS ROUTES ==============

@api_router.post("/processes", response_model=ProcessResponse)
async def create_process(data: ProcessCreate, user: dict = Depends(get_current_user)):
    if user["role"] != UserRole.CLIENTE:
        raise HTTPException(status_code=403, detail="Apenas clientes podem criar processos")
    
    process_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    process_doc = {
        "id": process_id,
        "client_id": user["id"],
        "client_name": user["name"],
        "client_email": user["email"],
        "process_type": data.process_type,
        "status": ProcessStatus.PEDIDO_INICIAL,
        "personal_data": data.personal_data.model_dump() if data.personal_data else None,
        "financial_data": data.financial_data.model_dump() if data.financial_data else None,
        "real_estate_data": None,
        "credit_data": None,
        "assigned_consultor_id": None,
        "assigned_mediador_id": None,
        "created_at": now,
        "updated_at": now
    }
    
    await db.processes.insert_one(process_doc)
    
    # Notify admins
    admins = await db.users.find({"role": UserRole.ADMIN}, {"_id": 0}).to_list(100)
    for admin in admins:
        await send_email_notification(
            admin["email"],
            "Novo Processo Criado",
            f"O cliente {user['name']} criou um novo processo de {data.process_type}."
        )
    
    return ProcessResponse(**{k: v for k, v in process_doc.items() if k != "_id"})

@api_router.get("/processes", response_model=List[ProcessResponse])
async def get_processes(user: dict = Depends(get_current_user)):
    query = {}
    
    if user["role"] == UserRole.CLIENTE:
        query["client_id"] = user["id"]
    elif user["role"] == UserRole.CONSULTOR:
        query["$or"] = [
            {"assigned_consultor_id": user["id"]},
            {"assigned_consultor_id": None, "process_type": {"$in": [ProcessType.IMOBILIARIA, ProcessType.AMBOS]}}
        ]
    elif user["role"] == UserRole.MEDIADOR:
        query["$or"] = [
            {"assigned_mediador_id": user["id"]},
            {"assigned_mediador_id": None, "process_type": {"$in": [ProcessType.CREDITO, ProcessType.AMBOS]}}
        ]
    # Admin sees all
    
    processes = await db.processes.find(query, {"_id": 0}).to_list(1000)
    return [ProcessResponse(**p) for p in processes]

@api_router.get("/processes/{process_id}", response_model=ProcessResponse)
async def get_process(process_id: str, user: dict = Depends(get_current_user)):
    process = await db.processes.find_one({"id": process_id}, {"_id": 0})
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    # Check access
    if user["role"] == UserRole.CLIENTE and process["client_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return ProcessResponse(**process)

@api_router.put("/processes/{process_id}", response_model=ProcessResponse)
async def update_process(process_id: str, data: ProcessUpdate, user: dict = Depends(get_current_user)):
    process = await db.processes.find_one({"id": process_id}, {"_id": 0})
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    # Role-based field access
    if user["role"] == UserRole.CLIENTE:
        if process["client_id"] != user["id"]:
            raise HTTPException(status_code=403, detail="Acesso negado")
        if data.personal_data:
            update_data["personal_data"] = data.personal_data.model_dump()
        if data.financial_data:
            update_data["financial_data"] = data.financial_data.model_dump()
    
    elif user["role"] == UserRole.CONSULTOR:
        if data.personal_data:
            update_data["personal_data"] = data.personal_data.model_dump()
        if data.financial_data:
            update_data["financial_data"] = data.financial_data.model_dump()
        if data.real_estate_data:
            update_data["real_estate_data"] = data.real_estate_data.model_dump()
        if data.status and data.status in [ProcessStatus.EM_ANALISE]:
            update_data["status"] = data.status
        # Auto-assign consultor
        if not process.get("assigned_consultor_id"):
            update_data["assigned_consultor_id"] = user["id"]
    
    elif user["role"] == UserRole.MEDIADOR:
        if data.personal_data:
            update_data["personal_data"] = data.personal_data.model_dump()
        if data.financial_data:
            update_data["financial_data"] = data.financial_data.model_dump()
        # Credit data only after bank authorization
        if data.credit_data:
            if process["status"] not in [ProcessStatus.AUTORIZACAO_BANCARIA, ProcessStatus.APROVADO]:
                raise HTTPException(status_code=400, detail="Dados de crédito só podem ser adicionados após autorização bancária")
            update_data["credit_data"] = data.credit_data.model_dump()
        if data.status and data.status in [ProcessStatus.EM_ANALISE, ProcessStatus.AUTORIZACAO_BANCARIA, ProcessStatus.APROVADO, ProcessStatus.REJEITADO]:
            update_data["status"] = data.status
            # Notify client on status change
            await send_email_notification(
                process["client_email"],
                f"Estado do Processo Atualizado",
                f"O estado do seu processo foi atualizado para: {data.status}"
            )
        # Auto-assign mediador
        if not process.get("assigned_mediador_id"):
            update_data["assigned_mediador_id"] = user["id"]
    
    elif user["role"] == UserRole.ADMIN:
        if data.personal_data:
            update_data["personal_data"] = data.personal_data.model_dump()
        if data.financial_data:
            update_data["financial_data"] = data.financial_data.model_dump()
        if data.real_estate_data:
            update_data["real_estate_data"] = data.real_estate_data.model_dump()
        if data.credit_data:
            update_data["credit_data"] = data.credit_data.model_dump()
        if data.status:
            update_data["status"] = data.status
    
    await db.processes.update_one({"id": process_id}, {"$set": update_data})
    updated = await db.processes.find_one({"id": process_id}, {"_id": 0})
    
    return ProcessResponse(**updated)

@api_router.post("/processes/{process_id}/assign")
async def assign_process(
    process_id: str, 
    consultor_id: Optional[str] = None,
    mediador_id: Optional[str] = None,
    user: dict = Depends(require_roles([UserRole.ADMIN]))
):
    process = await db.processes.find_one({"id": process_id})
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if consultor_id:
        consultor = await db.users.find_one({"id": consultor_id, "role": UserRole.CONSULTOR})
        if not consultor:
            raise HTTPException(status_code=404, detail="Consultor não encontrado")
        update_data["assigned_consultor_id"] = consultor_id
    
    if mediador_id:
        mediador = await db.users.find_one({"id": mediador_id, "role": UserRole.MEDIADOR})
        if not mediador:
            raise HTTPException(status_code=404, detail="Mediador não encontrado")
        update_data["assigned_mediador_id"] = mediador_id
    
    await db.processes.update_one({"id": process_id}, {"$set": update_data})
    return {"message": "Processo atribuído com sucesso"}

# ============== DEADLINE ROUTES ==============

@api_router.post("/deadlines", response_model=DeadlineResponse)
async def create_deadline(data: DeadlineCreate, user: dict = Depends(get_current_user)):
    if user["role"] == UserRole.CLIENTE:
        raise HTTPException(status_code=403, detail="Clientes não podem criar prazos")
    
    # Verify process exists
    process = await db.processes.find_one({"id": data.process_id}, {"_id": 0})
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    
    deadline_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    deadline_doc = {
        "id": deadline_id,
        "process_id": data.process_id,
        "title": data.title,
        "description": data.description,
        "due_date": data.due_date,
        "priority": data.priority,
        "completed": False,
        "created_by": user["id"],
        "created_at": now
    }
    
    await db.deadlines.insert_one(deadline_doc)
    
    # Notify client
    await send_email_notification(
        process["client_email"],
        f"Novo Prazo: {data.title}",
        f"Foi adicionado um novo prazo ao seu processo: {data.title} - Data limite: {data.due_date}"
    )
    
    return DeadlineResponse(**{k: v for k, v in deadline_doc.items() if k != "_id"})

@api_router.get("/deadlines", response_model=List[DeadlineResponse])
async def get_deadlines(process_id: Optional[str] = None, user: dict = Depends(get_current_user)):
    query = {}
    
    if process_id:
        query["process_id"] = process_id
    elif user["role"] == UserRole.CLIENTE:
        # Get client's processes
        processes = await db.processes.find({"client_id": user["id"]}, {"id": 1, "_id": 0}).to_list(1000)
        process_ids = [p["id"] for p in processes]
        query["process_id"] = {"$in": process_ids}
    
    deadlines = await db.deadlines.find(query, {"_id": 0}).to_list(1000)
    return [DeadlineResponse(**d) for d in deadlines]

@api_router.put("/deadlines/{deadline_id}", response_model=DeadlineResponse)
async def update_deadline(deadline_id: str, data: DeadlineUpdate, user: dict = Depends(get_current_user)):
    if user["role"] == UserRole.CLIENTE:
        raise HTTPException(status_code=403, detail="Clientes não podem editar prazos")
    
    deadline = await db.deadlines.find_one({"id": deadline_id}, {"_id": 0})
    if not deadline:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    
    update_data = {}
    if data.title is not None:
        update_data["title"] = data.title
    if data.description is not None:
        update_data["description"] = data.description
    if data.due_date is not None:
        update_data["due_date"] = data.due_date
    if data.priority is not None:
        update_data["priority"] = data.priority
    if data.completed is not None:
        update_data["completed"] = data.completed
    
    if update_data:
        await db.deadlines.update_one({"id": deadline_id}, {"$set": update_data})
    
    updated = await db.deadlines.find_one({"id": deadline_id}, {"_id": 0})
    return DeadlineResponse(**updated)

@api_router.delete("/deadlines/{deadline_id}")
async def delete_deadline(deadline_id: str, user: dict = Depends(require_roles([UserRole.CONSULTOR, UserRole.MEDIADOR, UserRole.ADMIN]))):
    result = await db.deadlines.delete_one({"id": deadline_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prazo não encontrado")
    return {"message": "Prazo eliminado"}

# ============== USER MANAGEMENT (ADMIN) ==============

@api_router.get("/users", response_model=List[UserResponse])
async def get_users(role: Optional[str] = None, user: dict = Depends(require_roles([UserRole.ADMIN]))):
    query = {}
    if role:
        query["role"] = role
    
    users = await db.users.find(query, {"_id": 0, "password": 0}).to_list(1000)
    return [UserResponse(**u) for u in users]

@api_router.post("/users", response_model=UserResponse)
async def create_user(data: UserCreate, user: dict = Depends(require_roles([UserRole.ADMIN]))):
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email já registado")
    
    if data.role not in [UserRole.CLIENTE, UserRole.CONSULTOR, UserRole.MEDIADOR, UserRole.ADMIN]:
        raise HTTPException(status_code=400, detail="Role inválido")
    
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    user_doc = {
        "id": user_id,
        "email": data.email,
        "password": hash_password(data.password),
        "name": data.name,
        "phone": data.phone,
        "role": data.role,
        "is_active": True,
        "created_at": now
    }
    
    await db.users.insert_one(user_doc)
    
    return UserResponse(
        id=user_id,
        email=data.email,
        name=data.name,
        phone=data.phone,
        role=data.role,
        created_at=now
    )

@api_router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, data: UserUpdate, user: dict = Depends(require_roles([UserRole.ADMIN]))):
    target_user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    
    update_data = {}
    if data.name is not None:
        update_data["name"] = data.name
    if data.phone is not None:
        update_data["phone"] = data.phone
    if data.role is not None:
        if data.role not in [UserRole.CLIENTE, UserRole.CONSULTOR, UserRole.MEDIADOR, UserRole.ADMIN]:
            raise HTTPException(status_code=400, detail="Role inválido")
        update_data["role"] = data.role
    if data.is_active is not None:
        update_data["is_active"] = data.is_active
    
    if update_data:
        await db.users.update_one({"id": user_id}, {"$set": update_data})
    
    updated = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
    return UserResponse(**updated)

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, user: dict = Depends(require_roles([UserRole.ADMIN]))):
    if user_id == user["id"]:
        raise HTTPException(status_code=400, detail="Não pode eliminar a própria conta")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Utilizador não encontrado")
    return {"message": "Utilizador eliminado"}

# ============== STATS ==============

@api_router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user)):
    stats = {}
    
    if user["role"] == UserRole.CLIENTE:
        stats["total_processes"] = await db.processes.count_documents({"client_id": user["id"]})
        stats["pending_deadlines"] = await db.deadlines.count_documents({
            "process_id": {"$in": [p["id"] for p in await db.processes.find({"client_id": user["id"]}, {"id": 1}).to_list(100)]},
            "completed": False
        })
    elif user["role"] in [UserRole.CONSULTOR, UserRole.MEDIADOR, UserRole.ADMIN]:
        stats["total_processes"] = await db.processes.count_documents({})
        stats["pending_processes"] = await db.processes.count_documents({"status": ProcessStatus.PEDIDO_INICIAL})
        stats["in_analysis"] = await db.processes.count_documents({"status": ProcessStatus.EM_ANALISE})
        stats["bank_authorization"] = await db.processes.count_documents({"status": ProcessStatus.AUTORIZACAO_BANCARIA})
        stats["approved"] = await db.processes.count_documents({"status": ProcessStatus.APROVADO})
        stats["rejected"] = await db.processes.count_documents({"status": ProcessStatus.REJEITADO})
        stats["total_deadlines"] = await db.deadlines.count_documents({})
        stats["pending_deadlines"] = await db.deadlines.count_documents({"completed": False})
    
    if user["role"] == UserRole.ADMIN:
        stats["total_users"] = await db.users.count_documents({})
        stats["clients"] = await db.users.count_documents({"role": UserRole.CLIENTE})
        stats["consultors"] = await db.users.count_documents({"role": UserRole.CONSULTOR})
        stats["mediadors"] = await db.users.count_documents({"role": UserRole.MEDIADOR})
    
    return stats

# ============== HEALTH CHECK ==============

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.processes.create_index("id", unique=True)
    await db.processes.create_index("client_id")
    await db.deadlines.create_index("id", unique=True)
    await db.deadlines.create_index("process_id")
    
    # Create default admin if not exists
    admin_exists = await db.users.find_one({"role": UserRole.ADMIN})
    if not admin_exists:
        admin_doc = {
            "id": str(uuid.uuid4()),
            "email": "admin@sistema.pt",
            "password": hash_password("admin123"),
            "name": "Administrador",
            "phone": None,
            "role": UserRole.ADMIN,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.users.insert_one(admin_doc)
        logger.info("Admin user created: admin@sistema.pt / admin123")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
