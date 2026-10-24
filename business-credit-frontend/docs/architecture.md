# Архитектура frontend MVP

```mermaid
flowchart TD
  UI["Браузер: подбор, сравнение, заявка"] --> State["Состояние и переходы: app.js"]
  State --> Storage["localStorage: синтетические данные"]
  State --> Mocks["Локальные реестр, БКИ, скоринг"]
  Docker["Nginx в Docker"] --> UI
```

В production команда должна перенести состояние, проверки и принятие решений на сервер. Предлагаемый REST-контракт — openapi.yaml. Сервер не реализован в этом frontend MVP. Отдельная банковская панель находится вне объёма работы.

```mermaid
stateDiagram-v2
  [*] --> DRAFT
  DRAFT --> SUBMITTED: Подтверждение и валидация
  SUBMITTED --> ENRICHING
  ENRICHING --> NEED_MORE_INFO: Не хватает данных
  NEED_MORE_INFO --> NEED_MORE_INFO: Неполный ответ
  NEED_MORE_INFO --> ENRICHING: Полный ответ
  ENRICHING --> CHECKS_UNAVAILABLE: Технический сбой
  CHECKS_UNAVAILABLE --> ENRICHING: Повтор
  ENRICHING --> SCORING: Проверки завершены
  SCORING --> APPROVED
  SCORING --> REJECTED
  SCORING --> COUNTER_OFFER
  COUNTER_OFFER --> APPROVED: Принята текущая версия
  COUNTER_OFFER --> CLOSED_BY_CLIENT: Отклонено
```

Ошибки полей сохраняют DRAFT. Отсутствие подходящего продукта происходит до заявки и не является REJECTED. После отказа или закрытия новый подбор создаёт новый DRAFT. Отдельная оценка риска содержит свободный поток и покрытие платежа. Кредитные правила затем учитывают возраст бизнеса, продукт, минимальную сумму и результаты тестового БКИ. Одобрение не означает подписание или выдачу денег.
