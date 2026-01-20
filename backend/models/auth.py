from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRole:
    CLIENTE = "cliente"
    CONSULTOR = "consultor"
    MEDIADOR = "mediador"
    CONSULTOR_MEDIADOR = "consultor_mediador"  # Can do both consultor and mediador tasks
    CEO = "ceo"  # Between admin and staff - can manage basic things + consultor/mediador tasks
    ADMIN = "admin"
    
    @classmethod
    def can_act_as_consultor(cls, role: str) -> bool:
        """Check if role can perform consultor tasks"""
        return role in [cls.CONSULTOR, cls.CONSULTOR_MEDIADOR, cls.CEO, cls.ADMIN]
    
    @classmethod
    def can_act_as_mediador(cls, role: str) -> bool:
        """Check if role can perform mediador tasks"""
        return role in [cls.MEDIADOR, cls.CONSULTOR_MEDIADOR, cls.CEO, cls.ADMIN]
    
    @classmethod
    def is_staff(cls, role: str) -> bool:
        """Check if role is staff (not cliente)"""
        return role != cls.CLIENTE


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
    onedrive_folder: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None
    role: str
    onedrive_folder: Optional[str] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    onedrive_folder: Optional[str] = None
