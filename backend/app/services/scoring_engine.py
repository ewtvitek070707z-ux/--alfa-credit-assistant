from datetime import datetime
from typing import Dict, Any, Tuple
from app.models import ApplicationStatus

class ScoringEngine:
    @staticmethod
    def calculate_score(
        requested_amount: float,
        requested_term: int,
        monthly_revenue: float,
        egrul_data: Dict[str, Any],
        bki_data: Dict[str, Any]
    ) -> int:
        score = 0

        # 1. Срок жизни компании
        reg_date_str = egrul_data.get("registration_date", "2024-01-01")
        try:
            reg_year = int(reg_date_str.split("-")[0])
            company_age_years = datetime.utcnow().year - reg_year
        except Exception:
            company_age_years = 1

        if company_age_years >= 3:
            score += 30
        elif company_age_years >= 1:
            score += 20
        else:
            score += 5

        # 2. Кредитная история БКИ
        if bki_data.get("delinquencies_active", False):
            score -= 40
        else:
            bki_score = bki_data.get("credit_score", 600)
            if bki_score >= 800:
                score += 35
            elif bki_score >= 650:
                score += 25
            elif bki_score >= 500:
                score += 15
            else:
                score += 5

        # 3. Долговая нагрузка
        monthly_payment_est = requested_amount / max(requested_term, 1)
        if monthly_revenue > 0:
            ratio = monthly_payment_est / monthly_revenue
            if ratio <= 0.15:
                score += 35
            elif ratio <= 0.35:
                score += 25
            elif ratio <= 0.50:
                score += 10

        return max(0, min(100, score))

    @classmethod
    def evaluate_decision(
        cls,
        score: int,
        requested_amount: float,
        requested_term: int,
        base_rate: float,
        egrul_data: Dict[str, Any],
        bki_data: Dict[str, Any],
        has_clarifications: bool = False
    ) -> Tuple[ApplicationStatus, Dict[str, Any]]:
        # 1. Стоп-фактор: просрочки
        if bki_data.get("delinquencies_active", False) or score < 35:
            return ApplicationStatus.REJECTED, {
                "decision_reason": "Отказ: обнаружена критическая кредитная нагрузка либо непогашенные просрочки в БКИ.",
                "approved_amount": 0.0,
                "approved_rate_pct": 0.0,
                "approved_term_months": 0
            }

        # 2. Запрос документов: если кредитная история отсутствует и документы еще не загружались
        if bki_data.get("rating_grade") == "NEW" and not has_clarifications:
            return ApplicationStatus.NEED_MORE_INFO, {
                "decision_reason": "Требуется уточнение: у компании отсутствует история в БКИ. Загрузите выписку со счета за последние 6 месяцев или налоговую декларацию.",
                "approved_amount": None,
                "approved_rate_pct": None,
                "approved_term_months": None
            }

        # 3. Контр-предложение (умеренный риск)
        if score < 75:
            counter_amount = round(requested_amount * 0.7, -3)
            counter_rate = base_rate + 2.5
            return ApplicationStatus.COUNTER_OFFER, {
                "decision_reason": f"Банк готов предоставить финансирование на специальных условиях: лимит скорректирован до {int(counter_amount):,} руб. со ставкой {counter_rate}% годовых для снижения долговой нагрузки.",
                "approved_amount": counter_amount,
                "approved_rate_pct": counter_rate,
                "approved_term_months": requested_term
            }

        # 4. Полное одобрение
        return ApplicationStatus.APPROVED, {
            "decision_reason": "Заявка одобрена в полном объеме по стандартной ставке продукта. Положительная кредитная история и стабильные показатели.",
            "approved_amount": requested_amount,
            "approved_rate_pct": base_rate,
            "approved_term_months": requested_term
        }