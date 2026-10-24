# Модель данных

В frontend все сущности локальны. Строки, вводимые пользователем, экранируются при HTML-рендеринге.

| Сущность | Поля |
|---|---|
| Product | id, name, description, rate, min/max, minTerm/maxTerm, goals[], tags[] |
| Selection | goal, amount, term, budget, urgency |
| Application | id, productId, filters (снимок Selection), status, company, inn, months, revenue, expenses, debt, consent, history[], files[], offerVersion |
| Event | status, note, time (ISO 8601) |
| Document metadata | name, size; содержимое не сохраняется |
| Risk result | free, coverage |
| Counter offer | amount, term, rate, version |
| Decision | reason / approvedAmount / acceptedOfferVersion |

Вспомогательные тестовые поля: scenario, retried, infoAccepted, infoText. Они не должны управляться клиентом в серверной реализации.

## Ограничения демомодели

Сумма: 100 000–30 000 000 ₽; срок: 6–84 мес.; дополнительно ограничения каждого продукта. Финансовые значения неотрицательные. Возраст бизнеса меньше 6 месяцев ведёт к отказу по правилам. ИНН: только 10 или 12 цифр; контрольные цифры не проверяются. Тестовый ИНН — 0000000000 и не обозначает реального клиента. Согласие обязательно перед отправкой. Пояснение минимум 20 символов. Прикрепление: PDF/JPEG/PNG до 5 МиБ, только метаданные.

Идемпотентность в демо: повторный submit для статуса не DRAFT игнорируется; повторная обработка не создаёт новый id. Сервер должен реализовать это атомарно с Idempotency-Key и проверкой версии. LocalStorage не обеспечивает безопасность, совместную работу, резервное копирование или серверную целостность.
