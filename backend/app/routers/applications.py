from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Application, Product, ApplicationStatus
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationClarify, ApplicationResponse
from app.services.egrul_mock import EgrulService
from app.services.bki_mock import BkiService
from app.services.scoring_engine import ScoringEngine

router = APIRouter(prefix="/api/applications", tags=["Кредитный конвейер (Заявки)"])

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED, summary="Создание черновика заявки")
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=400, detail=f"Продукт '{payload.product_id}' не найден.")

    # Предзаполняем имя компании из мока ЕГРЮЛ
    egrul_info = EgrulService.get_company_info(payload.inn)
    company_name = egrul_info.get("company_name", "Синтетическая компания")

    app_obj = Application(
        inn=payload.inn,
        company_name=company_name,
        contact_name=payload.contact_name,
        product_id=payload.product_id,
        requested_amount=payload.requested_amount,
        requested_term_months=payload.requested_term_months,
        monthly_revenue=payload.monthly_revenue,
        loan_purpose=payload.loan_purpose,
        status=ApplicationStatus.DRAFT
    )
    db.add(app_obj)
    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.get("/{app_id}", response_model=ApplicationResponse, summary="Получить статус и данные заявки")
def get_application(app_id: int, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return app_obj

@router.put("/{app_id}", response_model=ApplicationResponse, summary="Обновление черновика заявки")
def update_application(app_id: int, payload: ApplicationUpdate, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if app_obj.status != ApplicationStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Редактирование доступно только в статусе черновика (DRAFT)")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(app_obj, field, value)

    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.post("/{app_id}/submit", response_model=ApplicationResponse, summary="Отправка заявки и запуск кредитного конвейера")
def submit_and_process_application(app_id: int, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if app_obj.status not in [ApplicationStatus.DRAFT, ApplicationStatus.NEED_MORE_INFO]:
        raise HTTPException(status_code=400, detail=f"Нельзя повторно запустить обработку из статуса {app_obj.status.value}")

    # ЭТАП 1: Обогащение данных (ЕГРЮЛ + БКИ)
    app_obj.status = ApplicationStatus.ENRICHING
    egrul_data = EgrulService.get_company_info(app_obj.inn)
    bki_data = BkiService.get_credit_history(app_obj.inn)
    app_obj.enrichment_data = {
        "egrul": egrul_data,
        "bki": bki_data
    }
    app_obj.company_name = egrul_data.get("company_name", app_obj.company_name)

    # ЭТАП 2: Скоринг
    app_obj.status = ApplicationStatus.SCORING
    score = ScoringEngine.calculate_score(
        requested_amount=app_obj.requested_amount,
        requested_term=app_obj.requested_term_months,
        monthly_revenue=app_obj.monthly_revenue,
        egrul_data=egrul_data,
        bki_data=bki_data
    )
    app_obj.scoring_score = score

    # ЭТАП 3: Принятие кредитного решения
    product = db.query(Product).filter(Product.id == app_obj.product_id).first()
    base_rate = product.base_rate_pct if product else 15.0

    has_clarifications = app_obj.clarification_notes is not None

    final_status, decision_details = ScoringEngine.evaluate_decision(
        score=score,
        requested_amount=app_obj.requested_amount,
        requested_term=app_obj.requested_term_months,
        base_rate=base_rate,
        egrul_data=egrul_data,
        bki_data=bki_data,
        has_clarifications=has_clarifications
    )

    app_obj.status = final_status
    app_obj.decision_reason = decision_details.get("decision_reason")
    app_obj.approved_amount = decision_details.get("approved_amount")
    app_obj.approved_rate_pct = decision_details.get("approved_rate_pct")
    app_obj.approved_term_months = decision_details.get("approved_term_months")

    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.post("/{app_id}/clarify", response_model=ApplicationResponse, summary="Загрузка документов/уточнений по запросу банка")
def clarify_application(app_id: int, payload: ApplicationClarify, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if app_obj.status != ApplicationStatus.NEED_MORE_INFO:
        raise HTTPException(status_code=400, detail="Запрос уточнений возможен только при статусе NEED_MORE_INFO")

    app_obj.clarification_notes = f"Тип: {payload.document_type}. Комментарий: {payload.document_description}"
    if payload.additional_monthly_revenue:
        app_obj.monthly_revenue += payload.additional_monthly_revenue

    # После предоставления документов повторно запускаем оценку
    return submit_and_process_application(app_id=app_id, db=db)

@router.post("/{app_id}/sign", response_model=ApplicationResponse, summary="Моделирование подписания договора клиентом")
def sign_application(app_id: int, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if app_obj.status not in [ApplicationStatus.APPROVED, ApplicationStatus.COUNTER_OFFER]:
        raise HTTPException(status_code=400, detail="Подписание возможно только при одобрении или принятии контр-предложения")

    app_obj.status = ApplicationStatus.SIGNED
    db.commit()
    db.refresh(app_obj)
    return app_obj

@router.post("/{app_id}/disburse", response_model=ApplicationResponse, summary="Моделирование перечисления кредитных средств")
def disburse_application(app_id: int, db: Session = Depends(get_db)):
    app_obj = db.query(Application).filter(Application.id == app_id).first()
    if not app_obj:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if app_obj.status != ApplicationStatus.SIGNED:
        raise HTTPException(status_code=400, detail="Выдача средств возможна только после подписания договора")

    app_obj.status = ApplicationStatus.DISBURSED
    db.commit()
    db.refresh(app_obj)
    return app_obj
