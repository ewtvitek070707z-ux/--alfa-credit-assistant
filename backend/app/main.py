from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import applications, products, news, mocks

# Создание таблиц БД при старте
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Умный кредитный кабинет предпринимателя — Альфа-Банк API",
    description="Цифровой кредитный конвейер для малого и микробизнеса (Хакатон 'Альфа-Будущее')",
    version="1.0.0"
)

# Настройка CORS для работы с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(products.router)
app.include_router(applications.router)
app.include_router(news.router)
app.include_router(mocks.router)

@app.get("/", summary="Health Check")
def root():
    return {
        "status": "online",
        "service": "Alfa Smart Credit Conveyor API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }
