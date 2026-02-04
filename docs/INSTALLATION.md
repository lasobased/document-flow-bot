# Инструкция по запуску Document Flow Bot

## Быстрый старт (Quick Start)

### 1. Проверка требований системы

```bash
# Проверка версии Python (требуется 3.10+)
python --version
# или
python3 --version
```

### 2. Создание виртуального окружения

```bash
# Переход в директорию проекта
cd document-flow-bot

# Создание виртуального окружения
python -m venv venv

# Активация окружения
# На Linux/Mac:
source venv/bin/activate

# На Windows:
venv\Scripts\activate
```

После активации в начале строки появится `(venv)`.

### 3. Установка зависимостей

```bash
# Установка всех необходимых библиотек
pip install -r requirements.txt
```

### 4. Запуск приложения

```bash
# Запуск Streamlit интерфейса
streamlit run src/main.py
```

Приложение откроется автоматически в браузере по адресу: `http://localhost:8501`

## Запуск тестов

### Запуск всех тестов

```bash
# Активируйте виртуальное окружение, затем:
pytest tests/ -v
```

### Запуск с покрытием кода

```bash
pytest tests/ --cov=src --cov-report=html
```

Отчет будет сохранен в `htmlcov/index.html`.

### Запуск конкретного теста

```bash
pytest tests/test_validation.py::TestDateValidators::test_valid_date_format -v
```

## Работа с проектом

### Структура файлов

```
document-flow-bot/
├── src/
│   ├── main.py                  # Streamlit интерфейс
│   ├── logic.py                 # Движок правил
│   ├── document_validators.py   # Валидаторы
│   └── mock_data.py             # Тестовые данные
├── data/
│   └── raw/
│       └── rules.json   # Настройки правил (можно редактировать)
├── tests/
│   └── test_validation.py
└── requirements.txt
```

### Редактирование правил

Откройте файл `data/raw/rules.json` и измените параметры:

```json
{
  "thresholds": {
    "min_amount": 0.01,        // Измените минимальную сумму
    "max_amount": 10000000.00, // Измените максимальную сумму
    "expiry_warning_days": 30  // За сколько дней предупреждать
  }
}
```

После изменения просто обновите страницу в браузере.

### Добавление нового тестового документа

Откройте `src/mock_data.py` и добавьте:

```python
my_test_document = {
    "document_type": "invoice",
    "document_number": "MY-TEST-001",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": 5000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}
```

## Использование интерфейса

### Режим 1: Custom Input (Ручной ввод)

1. Выберите "Custom Input" в боковом меню
2. Заполните поля документа
3. Нажмите "Validate Document"
4. Просмотрите результаты валидации

### Режим 2: Test Predefined Cases (Готовые тесты)

1. Выберите "Test Predefined Cases"
2. Выберите категорию: Valid, Errors или Warnings
3. Раскройте нужный тест
4. Нажмите "Run Test"

### Режим 3: Batch Validation (Пакетная обработка)

Функционал будет добавлен в следующих версиях.

## Типичные проблемы и решения

### Ошибка: "ModuleNotFoundError: No module named 'streamlit'"

**Решение:**
```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate  # или venv\Scripts\activate на Windows

# Переустановите зависимости
pip install -r requirements.txt
```

### Ошибка: "FileNotFoundError: Rules file not found"

**Решение:**
```bash
# Убедитесь, что запускаете из корня проекта
cd document-flow-bot
streamlit run src/main.py
```

### Streamlit не открывается автоматически

**Решение:**
Откройте вручную в браузере: `http://localhost:8501`

### Порт 8501 занят

**Решение:**
```bash
# Запустите на другом порту
streamlit run src/main.py --server.port 8502
```

## Git команды

### Инициализация репозитория

```bash
# Инициализация Git
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Rule-Based validation system"

# Добавление удаленного репозитория
git remote add origin <your-github-url>

# Отправка в GitHub
git push -u origin main
```

### Обновление репозитория

```bash
# Добавить изменения
git add .

# Создать коммит
git commit -m "Add Rule-Based logic for Lab 2"

# Отправить в GitHub
git push
```

## Дополнительные команды

### Проверка качества кода

```bash
# Форматирование с Black
black src/

# Проверка стиля с Flake8
flake8 src/ --max-line-length=100

# Проверка типов с MyPy
mypy src/
```

### Деактивация виртуального окружения

```bash
deactivate
```

## Контакты и поддержка

Если возникли проблемы:
1. Проверьте FAQ выше
2. Посмотрите логи в терминале
3. Создайте Issue в GitHub репозитории

---

**Версия**: 1.0  
**Последнее обновление**: 2024-02-04
