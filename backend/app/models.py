from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class ApplicationStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ENRICHING = "ENRICHING"
    SCORING = "SCORING"
    APPROVED = "APPROVED"
    COUNTER_OFFER = "COUNTER_OFFER"
    NEED_MORE_INFO = "NEED_MORE_INFO"
    REJECTED = "REJECTED"
    SIGNED = "SIGNED"
    DISBURSED = "DISBURSED"

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    min_amount = Column(Float, nullable=False)
    max_amount = Column(Float, nullable=False)
    min_term_months = Column(Integer, nullable=False)
    max_term_months = Column(Integer, nullable=False)
    base_rate_pct = Column(Float, nullable=False)

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inn = Column(String(12), nullable=False, index=True)
    company_name = Column(String, nullable=True)
    contact_name = Column(String, nullable=True)
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    
    # Financial request
    requested_amount = Column(Float, nullable=False)
    requested_term_months = Column(Integer, nullable=False)
    monthly_revenue = Column(Float, nullable=False, default=0.0)
    loan_purpose = Column(String, nullable=True)

    # Conveyor State
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.DRAFT, nullable=False)
    scoring_score = Column(Integer, nullable=True)
    
    # Final conditions
    approved_amount = Column(Float, nullable=True)
    approved_rate_pct = Column(Float, nullable=True)
    approved_term_months = Column(Integer, nullable=True)
    
    decision_reason = Column(Text, nullable=True)
    clarification_notes = Column(Text, nullable=True)
    enrichment_data = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product")
