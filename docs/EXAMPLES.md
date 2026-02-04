# Примеры использования Document Flow Bot

## Пример 1: Валидация простой накладной

### Входные данные

```python
invoice = {
    "document_type": "invoice",
    "document_number": "INV-2024-0001",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-20",
    "total_amount": 15000.50,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}
```

### Результат валидации

```
[OK] Document passed all validation checks for 'invoice' document
```

### Детальный отчет

```
✓ is_signed: Document is signed
✓ document_type: OK
✓ required_fields: OK
✓ issue_date: OK
✓ inn: OK
✓ amount: OK
```

---

## Пример 2: Обнаружение просроченного документа

### Входные данные

```python
expired_contract = {
    "document_type": "contract",
    "document_number": "DOG-2023-999",
    "issue_date": "2023-12-01",
    "expiry_date": "2024-01-15",  # Просрочен
    "total_amount": 250000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}
```

### Результат валидации

```
[ERROR] Document has expired (Date is in the past: 2024-01-15)
```

**Пояснение**: Система обнаружила, что срок действия документа истек.

---

## Пример 3: Некорректный ИНН

### Входные данные

```python
invalid_inn = {
    "document_type": "invoice",
    "document_number": "INV-2024-0003",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": 5000.00,
    "inn": "123456",  # Неверная длина
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}
```

### Результат валидации

```
[ERROR] INN format is invalid (INN length must be 10 or 12, got 6)
```

**Пояснение**: ИНН должен быть 10 цифр (юр. лицо) или 12 цифр (физ. лицо).

---

## Пример 4: Предупреждение о скором истечении

### Входные данные

```python
expiring_soon = {
    "document_type": "contract",
    "document_number": "DOG-2024-046",
    "issue_date": "2024-01-15",
    "expiry_date": "2024-02-19",  # Истекает через 15 дней
    "total_amount": 100000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}
```

### Результат валидации

```
[WARNING] Document expires within 30 days (Document expires in 15 days)
```

**Пояснение**: Документ все еще действителен, но скоро истечет.

---

## Пример 5: Неподписанный документ

### Входные данные

```python
unsigned = {
    "document_type": "invoice",
    "document_number": "INV-2024-0002",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": 10000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": False  # Не подписан
}
```

### Результат валидации

```
[ERROR] Document must be digitally signed
```

**Пояснение**: Критическая проверка - документ должен быть подписан.

---

## Пример 6: Сумма вне диапазона

### Входные данные

```python
negative_amount = {
    "document_type": "invoice",
    "document_number": "INV-2024-0004",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": -1000.00,  # Отрицательная сумма
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}
```

### Результат валидации

```
[ERROR] Amount is outside allowed range (Amount -1000.0 is below minimum 0.01)
```

**Пояснение**: Сумма не может быть отрицательной.

---

## Пример 7: Запрещенный тип документа

### Входные данные

```python
blacklisted = {
    "document_type": "draft",  # Черновик не разрешен
    "document_number": "DRAFT-001",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": 1000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}
```

### Результат валидации

```
[ERROR] Document type not allowed (Document type 'draft' is blacklisted)
```

**Пояснение**: Система работает только с официальными документами.

---

## Пример 8: Большая сумма (предупреждение)

### Входные данные

```python
large_amount = {
    "document_type": "contract",
    "document_number": "DOG-2024-047",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-20",
    "total_amount": 9500000.00,  # Близко к лимиту 10M
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}
```

### Результат валидации

```
[WARNING] Unusually large amount detected (Large amount detected: 9500000.0 (threshold: 9000000.0))
```

**Пояснение**: Сумма близка к максимально допустимой, требует внимания.

---

## Использование в коде

### Простая валидация

```python
from logic import check_rules

# Ваш документ
document = {
    "document_type": "invoice",
    "document_number": "INV-001",
    "issue_date": "2024-02-04",
    "total_amount": 1000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

# Запуск валидации
result = check_rules(document)

# Обработка результата
if "[ERROR]" in result:
    print(f"Validation failed: {result}")
elif "[WARNING]" in result:
    print(f"Warning: {result}")
else:
    print(f"Success: {result}")
```

### Детальный отчет

```python
from logic import get_validation_summary

# Получаем детальную информацию
summary = get_validation_summary(document)

# Вывод результатов
print(f"Document Type: {summary['document_type']}")
print(f"Overall Status: {summary['overall_status']}")

for check_name, check_result in summary['checks'].items():
    print(f"{check_name}: {check_result['status']} - {check_result['message']}")
```

---

## Настройка правил

Отредактируйте `data/raw/rules.json` для изменения поведения системы:

### Изменение лимитов

```json
{
  "thresholds": {
    "min_amount": 1.00,          // Новый минимум
    "max_amount": 5000000.00,    // Новый максимум
    "expiry_warning_days": 14    // Предупреждать за 14 дней
  }
}
```

### Добавление нового типа документа

```json
{
  "document_types": {
    "allowed": ["invoice", "contract", "act", "receipt", "statement"],
    "blacklisted": ["draft", "template"]
  },
  "required_fields": {
    "statement": ["document_number", "issue_date", "total_amount"]
  }
}
```

---

## Интеграция с другими системами

### Пример REST API endpoint (Flask)

```python
from flask import Flask, request, jsonify
from logic import check_rules

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_document():
    document = request.json
    result = check_rules(document)
    
    return jsonify({
        'status': 'error' if '[ERROR]' in result else 'success',
        'message': result
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### Пример обработки CSV файла

```python
import csv
from logic import check_rules

def validate_csv(filepath):
    results = []
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            document = {
                'document_type': row['type'],
                'document_number': row['number'],
                'issue_date': row['date'],
                'total_amount': float(row['amount']),
                'inn': row['inn'],
                'is_signed': row['signed'] == 'True',
                'required_fields': ['document_number', 'issue_date', 'total_amount', 'inn']
            }
            
            result = check_rules(document)
            results.append({
                'document': row['number'],
                'result': result
            })
    
    return results
```

---

**Документация**: v1.0  
**Дата**: 2024-02-04
