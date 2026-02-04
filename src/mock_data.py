"""
Mock data для тестирования системы валидации документов.
Содержит примеры корректных и некорректных документов.
"""

from datetime import datetime, timedelta

# Вычисляем даты относительно текущей даты
TODAY = datetime.now().strftime("%Y-%m-%d")
TOMORROW = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
NEXT_MONTH = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
EXPIRED = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
EXPIRING_SOON = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")

# ========================================
# КОРРЕКТНЫЕ ДОКУМЕНТЫ (ДОЛЖНЫ ПРОЙТИ)
# ========================================

valid_invoice = {
    "document_type": "invoice",
    "document_number": "INV-2024-0001",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": 15000.50,
    "inn": "7743013902",  # 10 цифр - юридическое лицо
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

valid_contract = {
    "document_type": "contract",
    "document_number": "DOG-2024-045",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": 500000.00,
    "inn": "526317984689",  # 12 цифр - физическое лицо
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

valid_act = {
    "document_type": "act",
    "document_number": "ACT-2024-123",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": 75000.00,
    "inn": "7707083893",
    "required_fields": ["document_number", "issue_date", "total_amount"],
    "is_signed": True
}

# ========================================
# НЕКОРРЕКТНЫЕ ДОКУМЕНТЫ (С ОШИБКАМИ)
# ========================================

# Критическая ошибка: документ не подписан
unsigned_document = {
    "document_type": "invoice",
    "document_number": "INV-2024-0002",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": 10000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": False  # ОШИБКА: не подписан
}

# Критическая ошибка: просроченный документ
expired_document = {
    "document_type": "contract",
    "document_number": "DOG-2023-999",
    "issue_date": "2023-12-01",
    "expiry_date": EXPIRED,  # ОШИБКА: срок истек
    "total_amount": 250000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

# Ошибка: некорректный ИНН
invalid_inn_document = {
    "document_type": "invoice",
    "document_number": "INV-2024-0003",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": 5000.00,
    "inn": "123",  # ОШИБКА: неверная длина ИНН
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

# Ошибка: сумма вне допустимого диапазона
invalid_amount_document = {
    "document_type": "invoice",
    "document_number": "INV-2024-0004",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": -1000.00,  # ОШИБКА: отрицательная сумма
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

# Ошибка: запрещенный тип документа
blacklisted_document = {
    "document_type": "draft",  # ОШИБКА: черновик не разрешен
    "document_number": "DRAFT-001",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": 1000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
    "is_signed": True
}

# Предупреждение: срок истекает скоро
expiring_soon_document = {
    "document_type": "contract",
    "document_number": "DOG-2024-046",
    "issue_date": "2024-01-15",
    "expiry_date": EXPIRING_SOON,  # ПРЕДУПРЕЖДЕНИЕ: истекает через 15 дней
    "total_amount": 100000.00,
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

# Предупреждение: очень большая сумма
large_amount_document = {
    "document_type": "contract",
    "document_number": "DOG-2024-047",
    "issue_date": TODAY,
    "expiry_date": NEXT_MONTH,
    "total_amount": 9500000.00,  # ПРЕДУПРЕЖДЕНИЕ: близко к лимиту
    "inn": "7743013902",
    "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
    "is_signed": True
}

# ========================================
# НАБОР ДЛЯ ТЕСТИРОВАНИЯ
# ========================================

all_test_cases = {
    "valid": [
        ("Valid Invoice", valid_invoice),
        ("Valid Contract", valid_contract),
        ("Valid Act", valid_act),
    ],
    "errors": [
        ("Unsigned Document", unsigned_document),
        ("Expired Document", expired_document),
        ("Invalid INN", invalid_inn_document),
        ("Invalid Amount", invalid_amount_document),
        ("Blacklisted Type", blacklisted_document),
    ],
    "warnings": [
        ("Expiring Soon", expiring_soon_document),
        ("Large Amount", large_amount_document),
    ]
}

# Документ по умолчанию для интерфейса
default_document = valid_invoice
