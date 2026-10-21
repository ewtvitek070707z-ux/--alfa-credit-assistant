from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from app.models import ApplicationStatus

class ProductSchema(BaseModel):
    id: str
    name: str
    description: str
    min_amount: float
    max_amount: float
    min_term_months: int
    max_term_months: int
    base_rate_pct: float

    class Config:
        from_attributes = True

class ApplicationCreate(BaseModel):
    inn: str = Field(..., min_length=10, max_length=12, example="7701234567")
    product_id: str = Field(..., example="working_capital")
    requested_amount: float = Field(..., gt=0, example=1500000.0)
    requested_term_months: int = Field(..., gt=0, example=12)
    monthly_revenue: float = Field(..., ge=0, example=2500000.0)
    loan_purpose: Optional[str] = Field("Пополнение оборотных средств", example="Закупка товара")
    contact_name: Optional[str] = Field("Иван Иванов", example="Иван Иванов")

class ApplicationUpdate(BaseModel):
    requested_amount: Optional[float] = None
    requested_term_months: Optional[int] = None
    monthly_revenue: Optional[float] = None
    loan_purpose: Optional[str] = None
    contact_name: Optional[str] = None

class ApplicationClarify(BaseModel):
    document_type: str = Field(..., example="tax_declaration")
    document_description: str = Field(..., example="Налоговая декларация за 3 квартал загружена")
    additional_monthly_revenue: Optional[float] = None

class ApplicationResponse(BaseModel):
    id: int
    inn: str
    company_name: Optional[str]
    contact_name: Optional[str]
    product_id: str
    requested_amount: float
    requested_term_months: int
    monthly_revenue: float
    loan_purpose: Optional[str]
    status: ApplicationStatus
    scoring_score: Optional[int]
    approved_amount: Optional[float]
    approved_rate_pct: Optional[float]
    approved_term_months: Optional[int]
    decision_reason: Optional[str]
    clarification_notes: Optional[str]
    enrichment_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NewsItem(BaseModel):
    id: int
    title: str
    category: str
    tag: str
    summary: str
    relevance_reason: str
