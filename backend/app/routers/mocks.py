from fastapi import APIRouter
from app.services.egrul_mock import EgrulService
from app.services.bki_mock import BkiService

router = APIRouter(prefix="/api/mocks", tags=["Инспекция моков (ЕГРЮЛ и БКИ)"])

@router.get("/egrul/{inn}", summary="Проверка данных в моке ЕГРЮЛ / ФНС")
def inspect_egrul(inn: str):
    return EgrulService.get_company_info(inn)

@router.get("/bki/{inn}", summary="Проверка кредитной истории в моке БКИ")
def inspect_bki(inn: str):
    return BkiService.get_credit_history(inn)
