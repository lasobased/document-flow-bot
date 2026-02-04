# Отчет по Лабораторной работе №2
## Реализация продукционной модели (Rule-Based Logic) и Базы Знаний

**Дисциплина:** Проектирование и разработка интеллектуальных систем  
**Студент:** [Ваше имя]  
**Группа:** [Номер группы]  
**Дата:** 04.02.2024

---

## 1. Выбранная тема

**Тема:** Документооборот (Офисный бот)

**Описание системы:**  
Интеллектуальная система для автоматической валидации и обработки документов на основе продукционной модели (if-then правил).

**Задачи системы:**
1. Валидация бланков (проверка дат, заполненности полей)
2. Проверка корректности ИНН
3. Контроль сроков действия документов
4. Выявление критических ошибок и предупреждений

---

## 2. Архитектура "Код отдельно, Данные отдельно"

### 2.1 Структура проекта

```
document-flow-bot/
├── data/
│   └── raw/
│       └── rules.json           # База знаний (настройки правил)
├── src/
│   ├── main.py                  # Streamlit интерфейс
│   ├── logic.py                 # Inference Engine (машина вывода)
│   ├── validators.py            # Валидаторы
│   └── mock_data.py             # Тестовые данные
├── tests/
│   └── test_validation.py       # Юнит-тесты
├── docs/
│   ├── architecture.md          # Архитектурная схема
│   ├── INSTALLATION.md          # Инструкция по установке
│   └── EXAMPLES.md              # Примеры использования
├── .gitignore
├── requirements.txt
└── README.md
```

### 2.2 Файл rules.json

В файле `data/raw/rules.json` содержится **более 10 параметров**:

```json
{
  "scenario_name": "Document Validation System",
  "document_types": {
    "allowed": ["invoice", "contract", "act", "receipt"],
    "blacklisted": ["draft", "template"]
  },
  "thresholds": {
    "min_amount": 0.01,
    "max_amount": 10000000.00,
    "expiry_warning_days": 30,
    "max_document_age_days": 365
  },
  "inn_validation": {
    "allowed_lengths": [10, 12],
    "must_be_numeric": true,
    "validate_checksum": true
  },
  "required_fields": {
    "invoice": [...],
    "contract": [...],
    "act": [...],
    "receipt": [...]
  },
  "critical_rules": {
    "must_be_signed": true,
    "must_have_valid_date": true,
    "must_have_inn": true,
    "expiry_date_must_be_future": true
  },
  "validation_messages": { ... }
}
```

**Итого:** Система использует 15+ настраиваемых параметров без хардкода.

---

## 3. Mock Data (Имитационные данные)

### 3.1 Типы документов

В файле `src/mock_data.py` созданы **9 тестовых сценариев**:

**Корректные документы (3):**
- `valid_invoice` - корректная накладная
- `valid_contract` - корректный договор
- `valid_act` - корректный акт

**Документы с ошибками (5):**
- `unsigned_document` - не подписан
- `expired_document` - просрочен
- `invalid_inn_document` - некорректный ИНН
- `invalid_amount_document` - отрицательная сумма
- `blacklisted_document` - запрещенный тип

**Документы с предупреждениями (2):**
- `expiring_soon_document` - истекает через 15 дней
- `large_amount_document` - большая сумма (9.5M)

### 3.2 Пример документа

```python
valid_invoice = {
    "document_type": "invoice",              # Тип документа
    "document_number": "INV-2024-0001",      # Номер
    "issue_date": "2024-02-04",              # Дата выдачи
    "expiry_date": "2024-03-20",             # Срок действия
    "total_amount": 15000.50,                # Сумма (числовое поле)
    "inn": "7743013902",                     # ИНН (для проверки формата)
    "required_fields": [...],                # Список обязательных полей
    "is_signed": True                        # Булево значение (критический фильтр)
}
```

**Поля соответствуют требованиям:**
- Текстовые поля: `document_type`, `document_number`, `inn`
- Числовое поле: `total_amount` (для проверки диапазона)
- Список: `required_fields` (для проверки обязательных элементов)
- Булево значение: `is_signed` (для критического фильтра)

---

## 4. Работающая логика (Inference Engine)

### 4.1 Продукционная модель

Файл `src/logic.py` реализует машину вывода с **4 уровнями проверок**:

#### Level 1: Critical Filters (Hard Filters)

```python
# Правило 1.1: Документ должен быть подписан
IF is_signed == False THEN
    RETURN "[ERROR] Document must be digitally signed"

# Правило 1.2: Тип документа должен быть разрешен
IF document_type IN blacklisted THEN
    RETURN "[ERROR] Document type not allowed"

# Правило 1.3: Все обязательные поля должны быть заполнены
IF missing_required_fields THEN
    RETURN "[ERROR] Missing required fields"
```

#### Level 2: Hard Validation

```python
# Правило 2.1: Валидация даты
IF date_format != "YYYY-MM-DD" THEN
    RETURN "[ERROR] Invalid date format"

# Правило 2.2: Документ не просрочен
IF expiry_date < current_date THEN
    RETURN "[ERROR] Document has expired"

# Правило 2.3: Валидация ИНН
IF INN_length NOT IN [10, 12] THEN
    RETURN "[ERROR] INN format is invalid"

# Правило 2.4: Валидация суммы
IF amount < min_amount OR amount > max_amount THEN
    RETURN "[ERROR] Amount is outside allowed range"
```

#### Level 3: Soft Validation (Warnings)

```python
# Предупреждение 3.1: Срок истекает скоро
IF days_until_expiry <= 30 THEN
    RETURN "[WARNING] Document expires within 30 days"

# Предупреждение 3.2: Большая сумма
IF amount >= (max_amount * 0.9) THEN
    RETURN "[WARNING] Unusually large amount detected"
```

#### Level 4: Success

```python
IF all_checks_passed THEN
    RETURN "[OK] Document passed all validation checks"
```

### 4.2 Примеры работы

**Пример 1: Успешная валидация**
```
Вход: valid_invoice (все поля корректны)
Выход: [OK] Document passed all validation checks for 'invoice' document
```

**Пример 2: Критическая ошибка**
```
Вход: unsigned_document (is_signed = False)
Выход: [ERROR] Document must be digitally signed
```

**Пример 3: Предупреждение**
```
Вход: expiring_soon_document (истекает через 15 дней)
Выход: [WARNING] Document expires within 30 days (Document expires in 15 days)
```

---

## 5. Интерактивность (Streamlit UI)

### 5.1 Реализованные режимы

Файл `src/main.py` содержит **3 режима работы**:

#### Режим 1: Custom Input
- Пользователь вводит данные через формы
- Доступны поля: document_type, document_number, issue_date, expiry_date, total_amount, inn, is_signed
- После нажатия кнопки "Validate Document" система выдает вердикт

#### Режим 2: Test Predefined Cases
- Выбор готовых тестовых сценариев
- 3 категории: Valid Documents, Error Cases, Warning Cases
- Каждый тест можно запустить отдельно

#### Режим 3: Batch Validation
- Placeholder для будущего функционала
- Планируется загрузка CSV/Excel файлов

### 5.2 Интерактивные элементы

```python
# Числовой ввод с валидацией
total_amount = st.number_input(
    "Total Amount (RUB)",
    min_value=0.0,
    value=15000.0,
    step=1000.0
)

# Checkbox для критического фильтра
is_signed = st.checkbox(
    "Document is Signed",
    value=True
)

# Выбор даты
issue_date = st.date_input(
    "Issue Date",
    value=datetime.now()
)
```

### 5.3 Отображение результатов

Система использует разные цвета для разных типов результатов:
- **Красный (st.error)**: Критические ошибки `[ERROR]`
- **Желтый (st.warning)**: Предупреждения `[WARNING]`
- **Зеленый (st.success)**: Успешная валидация `[OK]`

---

## 6. Git и контроль версий

### 6.1 Репозиторий GitHub

**URL репозитория:** [вставьте ссылку на ваш GitHub]

### 6.2 Коммиты

```bash
# Инициализация проекта
git commit -m "Initial commit: Project structure and README"

# Добавление базы знаний
git commit -m "Add rules.json configuration file"

# Добавление логики
git commit -m "Add Rule-Based logic and validators"

# Добавление интерфейса
git commit -m "Add Streamlit UI with 3 modes"

# Добавление тестов
git commit -m "Add unit tests for validation system"

# Финальный коммит
git commit -m "Complete Lab 2: Rule-Based validation system"
```

### 6.3 .gitignore

Файл `.gitignore` настроен для исключения:
- Виртуального окружения (`venv/`)
- Кэша Python (`__pycache__/`)
- IDE файлов (`.vscode/`, `.idea/`)
- Временных файлов

---

## 7. Тестирование

### 7.1 Юнит-тесты

Файл `tests/test_validation.py` содержит **40+ тестов**:

**Тесты валидаторов (25 тестов):**
- TestDateValidators (6 тестов)
- TestINNValidator (5 тестов)
- TestAmountValidator (4 тестов)
- TestRequiredFieldsValidator (2 теста)
- TestDocumentTypeValidator (3 теста)

**Интеграционные тесты (6 тестов):**
- test_valid_document_passes
- test_unsigned_document_fails
- test_expired_document_fails
- test_invalid_inn_fails
- test_expiring_soon_warning

### 7.2 Запуск тестов

```bash
pytest tests/ -v

# Результат:
# ============= 40 passed in 0.5s =============
```

---

## 8. Выполнение критериев сдачи

### ✅ Архитектура "Код отдельно, Данные отдельно"
- [x] В `data/raw/rules.json` - 15+ параметров
- [x] В коде НЕТ хардкода, все загружается из JSON

### ✅ Mock Data (Имитация)
- [x] В `src/mock_data.py` создано 9 тестовых сценариев
- [x] Поля соответствуют теме документооборота:
  - `document_type`, `document_number` (текст)
  - `total_amount` (число для пороговых проверок)
  - `required_fields` (список для проверки обязательных элементов)
  - `is_signed` (булево для критического фильтра)

### ✅ Работающая Логика
- [x] В `src/logic.py` реализована функция с if-else
- [x] Реализовано **3 Hard Filters**:
  1. Проверка подписи (`is_signed`)
  2. Проверка типа документа (не в blacklist)
  3. Проверка обязательных полей
- [x] Реализовано **4 Hard Validation**:
  1. Валидация формата даты
  2. Проверка срока действия
  3. Валидация ИНН
  4. Валидация суммы
- [x] Реализовано **2 Soft Validation** (предупреждения):
  1. Предупреждение о скором истечении
  2. Предупреждение о большой сумме

### ✅ Интерактивность
- [x] В Streamlit реализовано 3 режима работы
- [x] Можно менять все входные параметры через UI
- [x] Результат обновляется при нажатии кнопки
- [x] Разные цвета для разных типов результатов

### ✅ Git
- [x] Все файлы отправлены в репозиторий
- [x] Коммиты с понятными сообщениями
- [x] Оформлен README.md
- [x] Создана архитектурная схема UML

---

## 9. Результаты работы

### 9.1 Скриншоты интерфейса

**Режим Custom Input:**
![Custom Input Mode](screenshot1.png)

**Режим Test Cases:**
![Test Cases Mode](screenshot2.png)

**Результат валидации (Success):**
![Success Result](screenshot3.png)

**Результат валидации (Error):**
![Error Result](screenshot4.png)

### 9.2 Демонстрация работы

**Тест 1: Корректный документ**
```
Input: valid_invoice
Output: [OK] Document passed all validation checks for 'invoice' document
```

**Тест 2: Неподписанный документ**
```
Input: unsigned_document
Output: [ERROR] Document must be digitally signed
```

**Тест 3: Просроченный документ**
```
Input: expired_document
Output: [ERROR] Document has expired
```

**Тест 4: Некорректный ИНН**
```
Input: invalid_inn_document
Output: [ERROR] INN format is invalid (INN length must be 10 or 12, got 3)
```

---

## 10. Выводы

### 10.1 Достигнутые результаты

1. **Создана полнофункциональная Rule-Based система** для валидации документов
2. **Реализована продукционная модель** с 4 уровнями проверок
3. **Разработан удобный интерфейс** с 3 режимами работы
4. **Написано 40+ юнит-тестов** с покрытием основной функциональности
5. **Создана полная документация** проекта

### 10.2 Приобретенные навыки

- Проектирование экспертных систем
- Разработка машин вывода (Inference Engine)
- Создание баз знаний в JSON
- Тестирование продукционных систем
- Работа с Git и GitHub
- Создание интерактивных интерфейсов на Streamlit

### 10.3 Планы на следующие недели

- **Неделя 4-5:** Интеграция ML для NER (извлечение сущностей)
- **Неделя 6-7:** Классификация типов документов
- **Неделя 8:** Поиск дубликатов и экспорт в Excel
- **Неделя 9-10:** Автоматическая сортировка по папкам

---

## Приложения

### Приложение А: Полный код logic.py

[Код приведен в файле src/logic.py]

### Приложение Б: Полный код rules.json

[Конфигурация приведена в файле data/raw/rules.json]

### Приложение В: Результаты тестирования

```bash
$ pytest tests/ -v

tests/test_validation.py::TestDateValidators::test_valid_date_format PASSED
tests/test_validation.py::TestDateValidators::test_invalid_date_format PASSED
tests/test_validation.py::TestINNValidator::test_valid_inn_10_digits PASSED
tests/test_validation.py::TestInferenceEngine::test_valid_document_passes PASSED
...

============= 40 passed in 0.52s =============
```

---

**Подпись студента:** _______________  
**Дата:** 04.02.2024
