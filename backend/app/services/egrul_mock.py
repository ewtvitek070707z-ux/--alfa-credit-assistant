from datetime import date
from typing import Dict, Any

# Синтетическая база данных ЕГРЮЛ / ФНС «Прозрачный бизнес»
SYNTHETIC_EGRUL_DB: Dict[str, Dict[str, Any]] = {
    "7701234567": {
        "inn": "7701234567",
        "ogrn": "1217700123456",
        "company_name": "ООО 'Ромашка Плюс'",
        "status": "ACTIVE",
        "registration_date": "2021-04-12",
        "okved": "47.11",
        "okved_name": "Торговля розничная преимущественно пищевыми продуктами",
        "ceo_name": "Иванов Иван Иванович",
        "tax_system": "USN",
        "is_reliable": True,
    },
    "7709876543": {
        "inn": "7709876543",
        "ogrn": "322774600987654",
        "company_name": "ИП Смирнов Алексей Васильевич",
        "status": "ACTIVE",
        "registration_date": "2023-01-15",
        "okved": "62.01",
        "okved_name": "Разработка компьютерного программного обеспечения",
        "ceo_name": "Смирнов Алексей Васильевич",
        "tax_system": "USN",
        "is_reliable": True,
    },
    "7705555555": {
        "inn": "7705555555",
        "ogrn": "1247700555555",
        "company_name": "ООО 'Новые Технологии'",
        "status": "ACTIVE",
        "registration_date": "2024-05-10",
        "okved": "56.10",
        "okved_name": "Деятельность ресторанов и услуги по доставке продуктов питания",
        "ceo_name": "Петров Петр Петрович",
        "tax_system": "OSNO",
        "is_reliable": True,
    },
    "7709999999": {
        "inn": "7709999999",
        "ogrn": "1197700999999",
        "company_name": "ООО 'СтройДефолт'",
        "status": "ACTIVE",
        "registration_date": "2019-11-20",
        "okved": "41.20",
        "okved_name": "Строительство жилых и нежилых зданий",
        "ceo_name": "Сидоров Сидор Сидорович",
        "tax_system": "OSNO",
        "is_reliable": False,
    }
}

class EgrulService:
    @staticmethod
    def get_company_info(inn: str) -> Dict[str, Any]:
        """Возвращает данные из ЕГРЮЛ/ФНС по ИНН или генерирует синтетический дефолт"""
        if inn in SYNTHETIC_EGRUL_DB:
            return SYNTHETIC_EGRUL_DB[inn]
        
        # Динамический дефолт для любого другого ИНН
        return {
            "inn": inn,
            "ogrn": f"122{inn[:10]}",
            "company_name": f"ООО 'Бизнес Партнер {inn[-4:]}'",
            "status": "ACTIVE",
            "registration_date": "2022-06-01",
            "okved": "46.90",
            "okved_name": "Торговля оптовая неспециализированная",
            "ceo_name": "Ковалев Андрей Михайлович",
            "tax_system": "USN",
            "is_reliable": True,
        }
