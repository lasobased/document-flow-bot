"""
Юнит-тесты для системы валидации документов.
Проверяют корректность работы validators и logic модулей.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime, timedelta
from document_validators import (
    validate_date_format,
    validate_date_not_past,
    validate_expiry_date,
    validate_inn,
    validate_amount,
    validate_required_fields,
    validate_document_type
)
from logic import check_rules


# ========================================
# ТЕСТЫ ВАЛИДАТОРОВ
# ========================================

class TestDateValidators:
    """Тесты для валидаторов дат"""
    
    def test_valid_date_format(self):
        """Тест корректного формата даты"""
        is_valid, msg = validate_date_format("2024-02-04")
        assert is_valid == True
        assert msg == "OK"
    
    def test_invalid_date_format(self):
        """Тест некорректного формата даты"""
        is_valid, msg = validate_date_format("04-02-2024")
        assert is_valid == False
        assert "Invalid date format" in msg
    
    def test_date_not_past_future(self):
        """Тест даты в будущем"""
        future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
        is_valid, msg = validate_date_not_past(future_date)
        assert is_valid == True
    
    def test_date_not_past_past(self):
        """Тест даты в прошлом"""
        past_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        is_valid, msg = validate_date_not_past(past_date)
        assert is_valid == False
        assert "past" in msg.lower()
    
    def test_expiry_after_issue(self):
        """Тест что срок действия после даты выдачи"""
        issue = "2024-01-01"
        expiry = "2024-12-31"
        is_valid, msg = validate_expiry_date(issue, expiry)
        assert is_valid == True
    
    def test_expiry_before_issue(self):
        """Тест что срок действия до даты выдачи (ошибка)"""
        issue = "2024-12-31"
        expiry = "2024-01-01"
        is_valid, msg = validate_expiry_date(issue, expiry)
        assert is_valid == False


class TestINNValidator:
    """Тесты для валидатора ИНН"""
    
    def test_valid_inn_10_digits(self):
        """Тест корректного ИНН юридического лица (10 цифр)"""
        is_valid, msg = validate_inn("7743013902")
        assert is_valid == True
    
    def test_valid_inn_12_digits(self):
        """Тест корректного ИНН физического лица (12 цифр)"""
        is_valid, msg = validate_inn("526317984689")
        assert is_valid == True
    
    def test_invalid_inn_length(self):
        """Тест некорректной длины ИНН"""
        is_valid, msg = validate_inn("123")
        assert is_valid == False
        assert "length" in msg.lower()
    
    def test_invalid_inn_non_digits(self):
        """Тест ИНН с буквами"""
        is_valid, msg = validate_inn("7743ABC902")
        assert is_valid == False
        assert "digits" in msg.lower()
    
    def test_empty_inn(self):
        """Тест пустого ИНН"""
        is_valid, msg = validate_inn("")
        assert is_valid == False


class TestAmountValidator:
    """Тесты для валидатора сумм"""
    
    def test_valid_amount_in_range(self):
        """Тест корректной суммы в диапазоне"""
        is_valid, msg = validate_amount(5000.0, 0.01, 10000000.0)
        assert is_valid == True
    
    def test_amount_below_minimum(self):
        """Тест суммы ниже минимума"""
        is_valid, msg = validate_amount(-100.0, 0.01, 10000000.0)
        assert is_valid == False
        assert "below minimum" in msg.lower()
    
    def test_amount_above_maximum(self):
        """Тест суммы выше максимума"""
        is_valid, msg = validate_amount(15000000.0, 0.01, 10000000.0)
        assert is_valid == False
        assert "exceeds maximum" in msg.lower()
    
    def test_amount_not_a_number(self):
        """Тест некорректного типа данных"""
        is_valid, msg = validate_amount("not a number", 0.01, 10000000.0)
        assert is_valid == False


class TestRequiredFieldsValidator:
    """Тесты для валидатора обязательных полей"""
    
    def test_all_fields_present(self):
        """Тест когда все поля присутствуют"""
        document = {
            "document_number": "INV-001",
            "issue_date": "2024-02-04",
            "total_amount": 1000.0
        }
        required = ["document_number", "issue_date", "total_amount"]
        is_valid, msg = validate_required_fields(document, required)
        assert is_valid == True
    
    def test_missing_fields(self):
        """Тест когда поля отсутствуют"""
        document = {
            "document_number": "INV-001"
        }
        required = ["document_number", "issue_date", "total_amount"]
        is_valid, msg = validate_required_fields(document, required)
        assert is_valid == False
        assert "missing" in msg.lower()


class TestDocumentTypeValidator:
    """Тесты для валидатора типа документа"""
    
    def test_allowed_type(self):
        """Тест разрешенного типа"""
        is_valid, msg = validate_document_type(
            "invoice",
            ["invoice", "contract"],
            ["draft"]
        )
        assert is_valid == True
    
    def test_blacklisted_type(self):
        """Тест запрещенного типа"""
        is_valid, msg = validate_document_type(
            "draft",
            ["invoice", "contract"],
            ["draft"]
        )
        assert is_valid == False
        assert "blacklisted" in msg.lower()
    
    def test_not_allowed_type(self):
        """Тест неразрешенного типа"""
        is_valid, msg = validate_document_type(
            "unknown",
            ["invoice", "contract"],
            ["draft"]
        )
        assert is_valid == False
        assert "not allowed" in msg.lower()


# ========================================
# ИНТЕГРАЦИОННЫЕ ТЕСТЫ
# ========================================

class TestInferenceEngine:
    """Тесты для машины вывода (Inference Engine)"""
    
    def test_valid_document_passes(self):
        """Тест что корректный документ проходит валидацию"""
        today = datetime.now().strftime("%Y-%m-%d")
        future = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")
        
        document = {
            "document_type": "invoice",
            "document_number": "INV-001",
            "issue_date": today,
            "expiry_date": future,
            "total_amount": 10000.0,
            "inn": "7743013902",
            "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
            "is_signed": True
        }
        
        result = check_rules(document)
        assert "[OK]" in result
    
    def test_unsigned_document_fails(self):
        """Тест что неподписанный документ отклоняется"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        document = {
            "document_type": "invoice",
            "document_number": "INV-002",
            "issue_date": today,
            "total_amount": 10000.0,
            "inn": "7743013902",
            "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
            "is_signed": False  # Ошибка
        }
        
        result = check_rules(document)
        assert "[ERROR]" in result
        assert "signed" in result.lower()
    
    def test_expired_document_fails(self):
        """Тест что просроченный документ отклоняется"""
        today = datetime.now().strftime("%Y-%m-%d")
        past = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        
        document = {
            "document_type": "contract",
            "document_number": "DOG-001",
            "issue_date": "2024-01-01",
            "expiry_date": past,  # Ошибка: просрочен
            "total_amount": 10000.0,
            "inn": "7743013902",
            "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
            "is_signed": True
        }
        
        result = check_rules(document)
        assert "[ERROR]" in result
    
    def test_invalid_inn_fails(self):
        """Тест что некорректный ИНН отклоняется"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        document = {
            "document_type": "invoice",
            "document_number": "INV-003",
            "issue_date": today,
            "total_amount": 10000.0,
            "inn": "123",  # Ошибка: неверная длина
            "required_fields": ["document_number", "issue_date", "total_amount", "inn"],
            "is_signed": True
        }
        
        result = check_rules(document)
        assert "[ERROR]" in result
        assert "inn" in result.lower()
    
    def test_expiring_soon_warning(self):
        """Тест предупреждения о скором истечении"""
        today = datetime.now().strftime("%Y-%m-%d")
        soon = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        
        document = {
            "document_type": "contract",
            "document_number": "DOG-002",
            "issue_date": "2024-01-01",
            "expiry_date": soon,  # Предупреждение: истекает скоро
            "total_amount": 10000.0,
            "inn": "7743013902",
            "required_fields": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
            "is_signed": True
        }
        
        result = check_rules(document)
        assert "[WARNING]" in result


# ========================================
# ЗАПУСК ТЕСТОВ
# ========================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
