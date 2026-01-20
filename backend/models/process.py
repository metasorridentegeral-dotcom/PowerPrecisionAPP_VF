from pydantic import BaseModel, EmailStr
from typing import Optional


class ProcessType:
    CREDITO = "credito"
    IMOBILIARIA = "imobiliaria"
    AMBOS = "ambos"


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


class PublicClientRegistration(BaseModel):
    name: str
    email: EmailStr
    phone: str
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
