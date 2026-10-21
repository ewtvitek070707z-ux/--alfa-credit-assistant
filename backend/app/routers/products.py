from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.schemas import ProductSchema

router = APIRouter(prefix="/api/products", tags=["Кредитные продукты"])

DEFAULT_PRODUCTS = [
    {
        "id": "working_capital",
        "name": "Оборотный кредит для бизнеса",
        "description": "Пополнение оборотных средств, закупка товаров, сырья и ликвидация кассовых разрывов.",
        "min_amount": 100000.0,
        "max_amount": 15000000.0,
        "min_term_months": 3,
        "max_term_months": 36,
        "base_rate_pct": 14.5
    },
    {
        "id": "investment",
        "name": "Инвестиционный кредит",
        "description": "Финансирование покупки оборудования, коммерческого транспорта и масштабирования точек.",
        "min_amount": 500000.0,
        "max_amount": 50000000.0,
        "min_term_months": 12,
        "max_term_months": 60,
        "base_rate_pct": 13.0
    },
    {
        "id": "express_micro",
        "name": "Экспресс-финансирование без залога",
        "description": "Быстрое решение за 5 минут для решения срочных операционных задач микробизнеса.",
        "min_amount": 50000.0,
        "max_amount": 3000000.0,
        "min_term_months": 1,
        "max_term_months": 12,
        "base_rate_pct": 16.5
    }
]

@router.get("", response_model=List[ProductSchema], summary="Каталог кредитных продуктов")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    if not products:
        # Автоматическая инициализация справочника
        for p_data in DEFAULT_PRODUCTS:
            db.add(Product(**p_data))
        db.commit()
        products = db.query(Product).all()
    return products
