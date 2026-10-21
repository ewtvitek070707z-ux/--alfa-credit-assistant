from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Application, ApplicationStatus
from app.schemas import NewsItem
from app.services.egrul_mock import EgrulService

router = APIRouter(prefix="/api/news", tags=["Персонализированная лента новостей"])

@router.get("", response_model=List[NewsItem], summary="Персонализированная новостная лента под профиль клиента")
def get_personalized_news(
    inn: Optional[str] = Query(None, description="ИНН компании клиента"),
    application_id: Optional[int] = Query(None, description="ID кредитной заявки"),
    db: Session = Depends(get_db)
):
    news: List[NewsItem] = []
    
    app_obj: Optional[Application] = None
    if application_id:
        app_obj = db.query(Application).filter(Application.id == application_id).first()
        if app_obj and not inn:
            inn = app_obj.inn

    egrul_data = EgrulService.get_company_info(inn) if inn else {}
    okved = egrul_data.get("okved", "")
    company_name = egrul_data.get("company_name", "Вашей компании")

    # 1. Новость на основе статуса заявки
    if app_obj:
        if app_obj.status in [ApplicationStatus.APPROVED, ApplicationStatus.SIGNED, ApplicationStatus.DISBURSED]:
            news.append(NewsItem(
                id=1,
                title="Поздравляем с одобрением: как эффективно распорядиться кредитными средствами",
                category="Финансовая грамотность",
                tag="Кредитование",
                summary="Гайд по управлению ликвидностью: распределение траншей и сокращение процентных расходов.",
                relevance_reason="Подобрано специально, так как ваша заявка успешно одобрена банком."
            ))
        elif app_obj.status == ApplicationStatus.COUNTER_OFFER:
            news.append(NewsItem(
                id=2,
                title="Оптимальная долговая нагрузка: почему скорректированный лимит безопаснее для бизнеса",
                category="Бизнес-аналитика",
                tag="Управление рисками",
                summary="Как рассчитывается коэффициент DSTI (платеж к доходу) и почему умеренный заем позволяет расти без кассовых разрывов.",
                relevance_reason="Подобрано под статус контр-предложения вашей заявки."
            ))
        elif app_obj.status == ApplicationStatus.NEED_MORE_INFO:
            news.append(NewsItem(
                id=3,
                title="Быстрая выгрузка отчетности из 1С и банка для экспресс-подтверждения заявки",
                category="Инструкции",
                tag="Бухгалтерия",
                summary="Пошаговая инструкция по формированию справки об остатках и выписки по расчетным счетам за 1 минуту.",
                relevance_reason="Актуально в связи с запросом дополнительных документов по заявке."
            ))

    # 2. Новости на основе ОКВЭД (отрасли)
    if okved.startswith("47"):  # Ритейл
        news.append(NewsItem(
            id=4,
            title="Тренды розничной торговли 2026: как снизить издержки на эквайринг и маркировку",
            category="Отраслевой дайджест",
            tag="Ритейл",
            summary="Анализ новых правил расчетов через СБП и способов оптимизации складских запасов в розничных точках.",
            relevance_reason=f"Подобрано для {company_name} по профилю деятельности (ОКВЭД 47 - Розничная торговля)."
        ))
    elif okved.startswith("62"):  # IT
        news.append(NewsItem(
            id=5,
            title="Налоговые преференции и гранты на разработку отечественного ПО в 2026 году",
            category="IT и инновации",
            tag="Технологии",
            summary="Обзор действующих льгот для аккредитованных IT-компаний и субсидированных кредитных ставок.",
            relevance_reason=f"Подобрано для {company_name} по профилю деятельности (ОКВЭД 62 - Разработка ПО)."
        ))
    elif okved.startswith("56"):  # Общепит
        news.append(NewsItem(
            id=6,
            title="Сезонность в HoReCa: как заведениям подготовиться к пиковому спросу",
            category="Ресторанный бизнес",
            tag="HoReCa",
            summary="Практические советы рестораторам по закупке оборудования в лизинг и управлению скоропортящимися запасами.",
            relevance_reason=f"Подобрано для {company_name} по профилю деятельности (ОКВЭД 56 - Общепит)."
        ))

    # 3. Общая новость от Альфа-Банка для бизнеса
    news.append(NewsItem(
        id=7,
        title="Альфа-Банк расширил линейку цифровых сервисов для субъектов МСП",
        category="Новости банка",
        tag="Альфа-Бизнес",
        summary="Предпринимателям стал доступен единый смарт-кабинет для онлайн-мониторинга оборотов, лимитов и налоговых платежей.",
        relevance_reason="Важная информация для всех клиентов малого и микробизнеса."
    ))

    return news
