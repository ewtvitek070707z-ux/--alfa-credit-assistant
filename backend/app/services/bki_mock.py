from typing import Dict, Any

# Синтетическая база кредитных историй (БКИ)
SYNTHETIC_BKI_DB: Dict[str, Dict[str, Any]] = {
    "7701234567": {
        "inn": "7701234567",
        "credit_score": 830,
        "active_loans_count": 1,
        "total_active_debt": 250000.0,
        "delinquencies_active": False,
        "historical_delinquencies_count": 0,
        "rating_grade": "A+",
        "payment_discipline_index": 0.98,
    },
    "7709876543": {
        "inn": "7709876543",
        "credit_score": 640,
        "active_loans_count": 2,
        "total_active_debt": 850000.0,
        "delinquencies_active": False,
        "historical_delinquencies_count": 1,
        "rating_grade": "B",
        "payment_discipline_index": 0.82,
    },
    "7705555555": {
        "inn": "7705555555",
        "credit_score": 520,
        "active_loans_count": 0,
        "total_active_debt": 0.0,
        "delinquencies_active": False,
        "historical_delinquencies_count": 0,
        "rating_grade": "NEW",  # Нет кредитной истории
        "payment_discipline_index": 0.50,
    },
    "7709999999": {
        "inn": "7709999999",
        "credit_score": 290,
        "active_loans_count": 4,
        "total_active_debt": 4800000.0,
        "delinquencies_active": True,
        "historical_delinquencies_count": 5,
        "rating_grade": "D",
        "payment_discipline_index": 0.25,
    }
}

class BkiService:
    @staticmethod
    def get_credit_history(inn: str) -> Dict[str, Any]:
        """Возвращает кредитную историю заемщика из БКИ"""
        if inn in SYNTHETIC_BKI_DB:
            return SYNTHETIC_BKI_DB[inn]
        
        # Дефолтный нейтральный профиль
        return {
            "inn": inn,
            "credit_score": 650,
            "active_loans_count": 1,
            "total_active_debt": 300000.0,
            "delinquencies_active": False,
            "historical_delinquencies_count": 0,
            "rating_grade": "B+",
            "payment_discipline_index": 0.85,
        }
