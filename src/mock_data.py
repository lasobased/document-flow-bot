"""
Mock Data - Набор тестовых документов для системы валидации.

Содержит 9 предопределенных сценариев:
- 3 валидных документа (OK)
- 4 документа с ошибками (ERROR)
- 2 документа с предупреждениями (WARNING)
"""

from datetime import datetime, timedelta

# ========================================
# ВАЛИДНЫЕ ДОКУМЕНТЫ (OK)
# ========================================

# ✅ Пример 1: Валидная накладная
VALID_INVOICE = {
    "document_type": "invoice",
    "document_number": "INV-2024-0001",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-20",
    "total_amount": 15000.50,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

# ✅ Пример 2: Валидный контракт
VALID_CONTRACT = {
    "document_type": "contract",
    "document_number": "DOG-2024-0042",
    "issue_date": "2024-02-04",
    "expiry_date": "2025-02-04",  # На 1 год
    "total_amount": 500000.00,
    "inn": "9876543210",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

# ✅ Пример 3: Валидный расходный ордер
VALID_RECEIPT = {
    "document_type": "receipt",
    "document_number": "RCP-2024-0042",
    "issue_date": "2024-02-04",
    "total_amount": 3500.00,
    "inn": "5555666677",
    "required_fields": ["document_number", "issue_date", "total_amount"],
    "is_signed": True
}

# ========================================
# ДОКУМЕНТЫ С ОШИБКАМИ (ERROR)
# ========================================

# ❌ Ошибка 1: Неподписанный документ
ERROR_UNSIGNED = {
    "document_type": "invoice",
    "document_number": "INV-2024-0002",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": 10000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": False  # ❌ Нет подписи
}

# ❌ Ошибка 2: Некорректный ИНН
ERROR_INVALID_INN = {
    "document_type": "invoice",
    "document_number": "INV-2024-0003",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": 5000.00,
    "inn": "123456",  # ❌ Только 6 цифр (должно быть 10 или 12)
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

# ❌ Ошибка 3: Просроченный документ
ERROR_EXPIRED = {
    "document_type": "contract",
    "document_number": "DOG-2023-999",
    "issue_date": "2023-12-01",
    "expiry_date": "2024-01-15",  # ❌ Дата в прошлом
    "total_amount": 250000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

# ❌ Ошибка 4: Запрещенный тип документа
ERROR_BLACKLISTED_TYPE = {
    "document_type": "draft",  # ❌ Черновик запрещен
    "document_number": "DRAFT-001",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-04",
    "total_amount": 1000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

# ========================================
# ДОКУМЕНТЫ С ПРЕДУПРЕЖДЕНИЯМИ (WARNING)
# ========================================

# ⚠️ Предупреждение 1: Скорое истечение
WARNING_EXPIRING_SOON = {
    "document_type": "contract",
    "document_number": "DOG-2024-046",
    "issue_date": "2024-01-15",
    "expiry_date": "2024-02-19",  # ⚠️ Истекает через ~15 дней
    "total_amount": 100000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

# ⚠️ Предупреждение 2: Большая сумма
WARNING_LARGE_AMOUNT = {
    "document_type": "contract",
    "document_number": "DOG-2024-047",
    "issue_date": "2024-02-04",
    "expiry_date": "2024-03-20",
    "total_amount": 9500000.00,  # ⚠️ Близко к лимиту 10M (80% от максимума)
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

# ========================================
# ГРУППЫ ТЕСТОВ (для удобства)
# ========================================

VALID_DOCUMENTS = {
    "valid_invoice": VALID_INVOICE,
    "valid_contract": VALID_CONTRACT,
    "valid_receipt": VALID_RECEIPT,
}

ERROR_DOCUMENTS = {
    "error_unsigned": ERROR_UNSIGNED,
    "error_invalid_inn": ERROR_INVALID_INN,
    "error_expired": ERROR_EXPIRED,
    "error_blacklisted_type": ERROR_BLACKLISTED_TYPE,
}

WARNING_DOCUMENTS = {
    "warning_expiring_soon": WARNING_EXPIRING_SOON,
    "warning_large_amount": WARNING_LARGE_AMOUNT,
}

ALL_DOCUMENTS = {
    **VALID_DOCUMENTS,
    **ERROR_DOCUMENTS,
    **WARNING_DOCUMENTS,
}

# ========================================
# УТИЛИТЫ
# ========================================

def get_all_test_cases():
    """Возвращает все тестовые документы с метаданными."""
    return {
        "valid": {
            "count": len(VALID_DOCUMENTS),
            "documents": VALID_DOCUMENTS,
            "expected_result": "[OK]"
        },
        "errors": {
            "count": len(ERROR_DOCUMENTS),
            "documents": ERROR_DOCUMENTS,
            "expected_result": "[ERROR]"
        },
        "warnings": {
            "count": len(WARNING_DOCUMENTS),
            "documents": WARNING_DOCUMENTS,
            "expected_result": "[WARNING]"
        }
    }

def get_test_by_name(name: str):
    """Получить тестовый документ по названию."""
    return ALL_DOCUMENTS.get(name)

def get_test_summary():
    """Вернуть статистику по тестам."""
    return {
        "total_tests": len(ALL_DOCUMENTS),
        "valid_tests": len(VALID_DOCUMENTS),
        "error_tests": len(ERROR_DOCUMENTS),
        "warning_tests": len(WARNING_DOCUMENTS),
    }

# ========================================
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ
# ========================================

if __name__ == "__main__":
    print("📋 Доступные тестовые документы:\n")
    
    print("✅ ВАЛИДНЫЕ документы:")
    for name in VALID_DOCUMENTS.keys():
        print(f"   - {name}")
    
    print("\n❌ ДОКУМЕНТЫ С ОШИБКАМИ:")
    for name in ERROR_DOCUMENTS.keys():
        print(f"   - {name}")
    
    print("\n⚠️ ДОКУМЕНТЫ С ПРЕДУПРЕЖДЕНИЯМИ:")
    for name in WARNING_DOCUMENTS.keys():
        print(f"   - {name}")
    
    print("\n📊 Статистика:")
    stats = get_test_summary()
    for key, value in stats.items():
        print(f"   {key}: {value}")
