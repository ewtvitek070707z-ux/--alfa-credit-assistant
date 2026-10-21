import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./credit_conveyor.db")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
