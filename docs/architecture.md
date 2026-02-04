# Архитектура системы Document Flow Bot

## 1. Общая архитектура (High-Level Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                          │
│                   (Streamlit Web App)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   main.py    │  │ validators.py│  │  mock_data.py│     │
│  │ (Controller) │  │  (Helpers)   │  │  (Test Data) │     │
│  └──────┬───────┘  └──────────────┘  └──────────────┘     │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────┐          │
│  │           logic.py (Inference Engine)        │          │
│  │  - load_rules()                              │          │
│  │  - check_rules(data)                         │          │
│  │  - validate_document(data)                   │          │
│  └──────────────────┬───────────────────────────┘          │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
│  ┌──────────────────────────────────────────────┐          │
│  │     data/raw/rules.json (Knowledge Base)     │          │
│  │  - thresholds                                │          │
│  │  - lists (whitelist/blacklist)               │          │
│  │  - critical_rules                            │          │
│  │  - validation_patterns                       │          │
│  └──────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## 2. Компонентная диаграмма (Component Diagram)

```
┌──────────────────────────────────────────────────────────────┐
│                        SYSTEM COMPONENTS                     │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  UI Component (main.py)                             │    │
│  │  - Input forms                                      │    │
│  │  - Result display                                   │    │
│  │  - Interactive controls                             │    │
│  └────────────────┬────────────────────────────────────┘    │
│                   │ uses                                     │
│                   ▼                                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Business Logic Component (logic.py)                │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │ RuleEngine                                  │    │    │
│  │  │  + load_rules(): dict                       │    │    │
│  │  │  + check_rules(data: dict): str             │    │    │
│  │  │  + validate_date(date: str): bool           │    │    │
│  │  │  + validate_inn(inn: str): bool             │    │    │
│  │  │  + check_required_fields(data: dict): bool  │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  └────────────────┬────────────────────────────────────┘    │
│                   │ reads                                    │
│                   ▼                                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Configuration Component (rules.json)               │    │
│  │  - Document types                                   │    │
│  │  - Validation rules                                 │    │
│  │  - Business constraints                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Validation Component (validators.py)               │    │
│  │  - DateValidator                                    │    │
│  │  - INNValidator                                     │    │
│  │  - AmountValidator                                  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Test Data Component (mock_data.py)                 │    │
│  │  - Sample invoices                                  │    │
│  │  - Sample contracts                                 │    │
│  │  - Edge cases                                       │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## 3. Диаграмма последовательности (Sequence Diagram)

```
User          Streamlit UI       RuleEngine         JSON Config
 │                 │                 │                    │
 │  Submit form    │                 │                    │
 ├────────────────>│                 │                    │
 │                 │                 │                    │
 │                 │  check_rules()  │                    │
 │                 ├────────────────>│                    │
 │                 │                 │                    │
 │                 │                 │  load_rules()      │
 │                 │                 ├───────────────────>│
 │                 │                 │                    │
 │                 │                 │  return rules dict │
 │                 │                 │<───────────────────┤
 │                 │                 │                    │
 │                 │                 │ [1] Check critical │
 │                 │                 │     filters        │
 │                 │                 │                    │
 │                 │                 │ [2] Validate dates │
 │                 │                 │                    │
 │                 │                 │ [3] Check amounts  │
 │                 │                 │                    │
 │                 │                 │ [4] Validate INN   │
 │                 │                 │                    │
 │                 │  return verdict │                    │
 │                 │<────────────────┤                    │
 │                 │                 │                    │
 │  Display result │                 │                    │
 │<────────────────┤                 │                    │
 │                 │                 │                    │
```

## 4. Диаграмма потока данных (Data Flow Diagram)

```
┌──────────────┐
│  User Input  │
│  (Document)  │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────┐
│  INPUT VALIDATION                  │
│  - Type check                      │
│  - Format check                    │
│  - Required fields present         │
└──────┬─────────────────────────────┘
       │
       ▼
┌────────────────────────────────────┐
│  CRITICAL FILTERS (Hard Filters)   │
│  ├─ is_signed == True?             │
│  ├─ document_type in allowed?      │
│  └─ required_fields complete?      │
└──────┬─────────────────────────────┘
       │
       ├─ FAIL ──> [ERROR: Critical check failed]
       │
       ▼ PASS
┌────────────────────────────────────┐
│  DATE VALIDATION                   │
│  ├─ Date format valid?             │
│  ├─ Date not in past?              │
│  └─ Expiry date > issue date?      │
└──────┬─────────────────────────────┘
       │
       ├─ FAIL ──> [ERROR: Date validation failed]
       │
       ▼ PASS
┌────────────────────────────────────┐
│  AMOUNT VALIDATION                 │
│  ├─ Amount > min_threshold?        │
│  ├─ Amount < max_threshold?        │
│  └─ Amount format correct?         │
└──────┬─────────────────────────────┘
       │
       ├─ FAIL ──> [WARNING: Amount out of range]
       │
       ▼ PASS
┌────────────────────────────────────┐
│  INN VALIDATION                    │
│  ├─ Length == 10 or 12?            │
│  ├─ Digits only?                   │
│  └─ Checksum valid?                │
└──────┬─────────────────────────────┘
       │
       ├─ FAIL ──> [ERROR: Invalid INN]
       │
       ▼ PASS
┌────────────────────────────────────┐
│  BLACKLIST CHECK                   │
│  └─ Document type not blacklisted? │
└──────┬─────────────────────────────┘
       │
       ▼
┌──────────────┐
│  SUCCESS     │
│  Document OK │
└──────────────┘
```

## 5. Диаграмма классов (Class Diagram)

```
┌─────────────────────────────────────┐
│         RuleEngine                  │
├─────────────────────────────────────┤
│ - rules: dict                       │
│ - validators: list[Validator]      │
├─────────────────────────────────────┤
│ + __init__()                        │
│ + load_rules(): dict                │
│ + check_rules(data: dict): str      │
│ + validate_all(data: dict): bool    │
└─────────────────┬───────────────────┘
                  │
                  │ uses
                  ▼
┌─────────────────────────────────────┐
│      <<abstract>>                   │
│        Validator                    │
├─────────────────────────────────────┤
│ + validate(value: any): bool        │
│ + get_error_message(): str          │
└─────────────────┬───────────────────┘
                  │
        ┌─────────┴─────────┬──────────────┐
        │                   │              │
        ▼                   ▼              ▼
┌──────────────┐   ┌──────────────┐  ┌──────────────┐
│DateValidator │   │INNValidator  │  │AmountValidator│
├──────────────┤   ├──────────────┤  ├──────────────┤
│+ validate()  │   │+ validate()  │  │+ validate()  │
│+ check_date()│   │+ checksum()  │  │+ in_range()  │
└──────────────┘   └──────────────┘  └──────────────┘
```

## 6. Модель данных документа

```
Document {
    document_type: string           // "invoice", "contract", "act"
    document_number: string         // Уникальный номер
    issue_date: string (ISO 8601)   // Дата выдачи
    expiry_date: string (ISO 8601)  // Срок действия
    total_amount: float             // Сумма
    inn: string                     // ИНН (10 или 12 цифр)
    required_fields: list[string]   // Обязательные поля
    is_signed: boolean              // Наличие подписи
    metadata: {
        created_by: string
        created_at: timestamp
        status: string
    }
}
```

## 7. Принципы работы системы

### 7.1 Продукционная модель (Rule-Based System)

Система работает на основе правил вида:
```
IF <condition> THEN <action>
```

Пример:
```
IF (is_signed == False) THEN 
    RETURN "ERROR: Document must be signed"
    
IF (expiry_date < current_date) THEN 
    RETURN "ERROR: Document expired"
    
IF (total_amount < min_threshold) THEN 
    RETURN "WARNING: Amount below minimum"
```

### 7.2 Порядок выполнения проверок

1. **Critical Filters** (останавливают выполнение)
2. **Hard Validation** (обязательные проверки)
3. **Soft Validation** (предупреждения)
4. **Business Logic** (специфичные правила)

### 7.3 Типы результатов

- `ERROR` - Критическая ошибка, документ отклонен
- `WARNING` - Предупреждение, требует внимания
- `SUCCESS` - Документ прошел все проверки

## 8. Расширяемость системы

### Добавление нового типа документа

1. Обновить `rules.json` с новыми правилами
2. Создать новый валидатор в `validators.py`
3. Добавить обработку в `logic.py`

### Добавление новой проверки

1. Описать правило в `rules.json`
2. Реализовать логику в `logic.py`
3. Добавить тест в `tests/`

---

**Версия документа**: 1.0  
**Дата**: 2024-02-04
