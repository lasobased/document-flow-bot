# QUICKSTART - Document Flow Bot

## Быстрый запуск за 3 минуты

### ВАЖНО: Исправление конфликта имен (если есть ошибка)

Если при запуске вы видите ошибку `ImportError: cannot import name 'validate_date_format' from 'validators'`, выполните:

**Windows PowerShell:**
```powershell
.\fix-windows.ps1
```

**Linux/Mac:**
```bash
./fix-linux.sh
```

Или примените исправления вручную согласно файлу `FIX_IMPORT_ERROR.md`.

---

### Шаг 1: Установка (30 секунд)

```bash
cd document-flow-bot
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

### Шаг 2: Запуск (10 секунд)

```bash
streamlit run src/main.py
```

Откроется браузер на `http://localhost:8501`

### Шаг 3: Тестирование (1 минута)

**В интерфейсе Streamlit:**

1. Выберите режим "Test Predefined Cases"
2. Выберите "Valid Documents"
3. Откройте "Valid Invoice"
4. Нажмите "Run Test"
5. Увидите: `[OK] Document passed all validation checks`

**Или запустите тесты в терминале:**

```bash
pytest tests/ -v
```

Результат: `40 passed in 0.5s`

---

## Что уже работает

- [x] Валидация 4 типов документов (invoice, contract, act, receipt)
- [x] 7+ правил валидации (подпись, даты, ИНН, суммы)
- [x] 3 режима работы (Custom Input, Test Cases, Batch)
- [x] 9 готовых тестовых сценариев
- [x] Детальные отчеты о валидации
- [x] 40+ юнит-тестов

---

## Примеры использования

### Пример 1: Валидация через UI

1. Откройте "Custom Input"
2. Заполните поля:
   - Document Type: invoice
   - Document Number: INV-001
   - Issue Date: сегодня
   - Total Amount: 10000
   - INN: 7743013902
   - Is Signed: ✓
3. Нажмите "Validate Document"

Результат: зеленое сообщение об успехе

### Пример 2: Проверка ошибки

1. Откройте "Custom Input"
2. Снимите галочку "Is Signed"
3. Нажмите "Validate Document"

Результат: красное сообщение `[ERROR] Document must be digitally signed`

### Пример 3: Запуск из кода

```python
from src.logic import check_rules

document = {
    "document_type": "invoice",
    "document_number": "INV-001",
    "issue_date": "2024-02-04",
    "total_amount": 1000.0,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

result = check_rules(document)
print(result)
# Output: [OK] Document passed all validation checks for 'invoice' document
```

---

## Настройка правил

Откройте `data/raw/rules.json` и измените:

```json
{
  "thresholds": {
    "min_amount": 0.01,        # Минимальная сумма
    "max_amount": 10000000.00, # Максимальная сумма
    "expiry_warning_days": 30  # За сколько дней предупреждать
  }
}
```

Изменения применятся автоматически при следующей валидации.

---

## Git и GitHub

### Инициализация репозитория

```bash
# Запустить автоматический скрипт
./git-setup.sh

# Или вручную:
git init
git add .
git commit -m "Initial commit: Rule-Based validation system"
```

### Отправка на GitHub

```bash
git remote add origin https://github.com/your-username/document-flow-bot.git
git branch -M main
git push -u origin main
```

---

## Типичные проблемы

**Проблема:** ModuleNotFoundError: No module named 'streamlit'  
**Решение:** Активируйте venv и запустите `pip install -r requirements.txt`

**Проблема:** FileNotFoundError: Rules file not found  
**Решение:** Запускайте из корня проекта: `streamlit run src/main.py`

**Проблема:** Port 8501 already in use  
**Решение:** `streamlit run src/main.py --server.port 8502`

---

## Полезные команды

```bash
# Запуск тестов с покрытием
pytest tests/ --cov=src --cov-report=html

# Проверка стиля кода
flake8 src/ --max-line-length=100

# Форматирование кода
black src/

# Просмотр логов Streamlit
streamlit run src/main.py --logger.level=debug
```

---

## Документация

- **README.md** - Общее описание проекта
- **docs/architecture.md** - Архитектура и UML диаграммы
- **docs/INSTALLATION.md** - Подробная инструкция по установке
- **docs/EXAMPLES.md** - Примеры использования
- **docs/LAB_REPORT.md** - Отчет по лабораторной работе

---

## Контрольный список сдачи (Lab 2)

- [x] Репозиторий на GitHub с README.md
- [x] Архитектурная схема (UML)
- [x] .gitignore настроен
- [x] Virtual Environment создано
- [x] Файл rules.json с 15+ параметрами
- [x] Нет хардкода в коде
- [x] Mock data с 9 тестовыми случаями
- [x] Поля соответствуют теме (document_type, amount, inn, is_signed)
- [x] Функция check_rules() с if-else
- [x] Минимум 1 Hard Filter (реализовано 3)
- [x] Streamlit интерфейс работает
- [x] Можно менять входные данные
- [x] Коммиты с понятными сообщениями

**Статус:** ✅ Все критерии выполнены

---

**Версия:** 1.0  
**Дата:** 2024-02-04  
**Время разработки:** Неделя 1-3
