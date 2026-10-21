import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # Инициализируем справочник продуктов
    client.get("/api/products")
    yield

def test_scenario_approved():
    """Тест профиля 'Ромашка Плюс': Одобрено в полном объеме"""
    # 1. Создание черновика
    resp = client.post("/api/applications", json={
        "inn": "7701234567",
        "product_id": "working_capital",
        "requested_amount": 1000000.0,
        "requested_term_months": 12,
        "monthly_revenue": 2000000.0,
        "loan_purpose": "Закупка товара"
    })
    assert resp.status_code == 201
    data = resp.json()
    app_id = data["id"]
    assert data["status"] == "DRAFT"
    assert data["company_name"] == "ООО 'Ромашка Плюс'"

    # 2. Запуск конвейера
    submit_resp = client.post(f"/api/applications/{app_id}/submit")
    assert submit_resp.status_code == 200
    res_data = submit_resp.json()
    assert res_data["status"] == "APPROVED"
    assert res_data["scoring_score"] >= 75
    assert res_data["approved_amount"] == 1000000.0

    # 3. Подписание и выдача
    sign_resp = client.post(f"/api/applications/{app_id}/sign")
    assert sign_resp.status_code == 200
    assert sign_resp.json()["status"] == "SIGNED"

    disb_resp = client.post(f"/api/applications/{app_id}/disburse")
    assert disb_resp.status_code == 200
    assert disb_resp.json()["status"] == "DISBURSED"

def test_scenario_counter_offer():
    """Тест профиля ИП Смирнов: Контр-предложение"""
    resp = client.post("/api/applications", json={
        "inn": "7709876543",
        "product_id": "working_capital",
        "requested_amount": 2000000.0,
        "requested_term_months": 12,
        "monthly_revenue": 800000.0
    })
    app_id = resp.json()["id"]

    submit_resp = client.post(f"/api/applications/{app_id}/submit")
    assert submit_resp.status_code == 200
    res_data = submit_resp.json()
    assert res_data["status"] == "COUNTER_OFFER"
    assert res_data["approved_amount"] < 2000000.0

def test_scenario_rejected():
    """Тест профиля ООО 'СтройДефолт': Отказ из-за долгов в БКИ"""
    resp = client.post("/api/applications", json={
        "inn": "7709999999",
        "product_id": "working_capital",
        "requested_amount": 5000000.0,
        "requested_term_months": 24,
        "monthly_revenue": 1000000.0
    })
    app_id = resp.json()["id"]

    submit_resp = client.post(f"/api/applications/{app_id}/submit")
    assert submit_resp.status_code == 200
    res_data = submit_resp.json()
    assert res_data["status"] == "REJECTED"
    assert "просрочки" in res_data["decision_reason"]

def test_personalized_news():
    """Тест персонализированных новостей по ИНН"""
    resp = client.get("/api/news?inn=7701234567")
    assert resp.status_code == 200
    news = resp.json()
    assert len(news) > 0
    # Проверяем наличие новости для ритейла (ОКВЭД 47)
    assert any("Розничная торговля" in item["relevance_reason"] for item in news)
