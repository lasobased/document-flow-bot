"""
Document Validators - Модуль валидации полей документов.
Содержит функции для проверки отдельных полей и бизнес-правил.
"""

from datetime import datetime, timedelta
from typing import Tuple, List


# ========================================
# ВАЛИДАЦИЯ ДАТ
# ========================================

def validate_date_format(date_str: str) -> Tuple[bool, str]:
    """
    Проверяет корректность формата даты (YYYY-MM-DD).
    
    Args:
        date_str: Строка с датой
        
    Returns:
        (True, "Valid date") если формат корректен
        (False, "Error message") если формат некорректен
    """
    if not date_str:
        return False, "Date is empty"
    
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, "Valid date format"
    except ValueError:
        return False, f"Invalid date format: '{date_str}'. Expected YYYY-MM-DD"


def validate_date_not_past(date_str: str) -> Tuple[bool, str]:
    """
    Проверяет, что дата не в прошлом.
    
    Args:
        date_str: Строка с датой в формате YYYY-MM-DD
        
    Returns:
        (True, message) если дата в будущем или сегодня
        (False, message) если дата в прошлом
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date_obj < today:
            days_ago = (today - date_obj).days
            return False, f"Date is {days_ago} days in the past"
        
        return True, "Date is valid (not in past)"
    except ValueError:
        return False, f"Cannot parse date: '{date_str}'"


def validate_expiry_date(issue_date: str, expiry_date: str) -> Tuple[bool, str]:
    """
    Проверяет, что срок действия больше даты выдачи.
    
    Args:
        issue_date: Дата выдачи
        expiry_date: Срок действия
        
    Returns:
        (True, message) если expiry_date > issue_date
        (False, message) если expiry_date <= issue_date
    """
    try:
        issue = datetime.strptime(issue_date, "%Y-%m-%d")
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
        
        if expiry <= issue:
            return False, f"Expiry date ({expiry_date}) must be after issue date ({issue_date})"
        
        return True, "Expiry date is valid"
    except ValueError as e:
        return False, f"Date parsing error: {str(e)}"


def check_expiry_warning(expiry_date: str, warning_days: int) -> Tuple[bool, str]:
    """
    Проверяет, не истекает ли срок действия в ближайшее время.
    
    Args:
        expiry_date: Срок действия
        warning_days: Количество дней для предупреждения
        
    Returns:
        (True, message) если срок истекает скоро
        (False, message) если срок не истекает скоро
    """
    try:
        expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_until_expiry = (expiry - today).days
        
        if 0 <= days_until_expiry <= warning_days:
            return True, f"Document expires in {days_until_expiry} days"
        
        return False, "Expiry date is not approaching"
    except ValueError:
        return False, f"Cannot parse expiry date: '{expiry_date}'"


# ========================================
# ВАЛИДАЦИЯ ИНН
# ========================================

def validate_inn(inn: str, allowed_lengths: List[int]) -> Tuple[bool, str]:
    """
    Проверяет корректность ИНН (Идентификационного Номера Налогоплательщика).
    
    Args:
        inn: ИНН в виде строки
        allowed_lengths: Список допустимых длин (обычно [10, 12])
        
    Returns:
        (True, message) если ИНН корректен
        (False, message) если ИНН некорректен
    """
    if not inn:
        return False, "INN is empty"
    
    # Проверка, что ИНН состоит только из цифр
    if not inn.isdigit():
        return False, f"INN must contain only digits, got: '{inn}'"
    
    # Проверка длины
    if len(inn) not in allowed_lengths:
        return False, f"INN length must be {' or '.join(map(str, allowed_lengths))}, got: {len(inn)}"
    
    return True, f"Valid INN ({len(inn)} digits)"


# ========================================
# ВАЛИДАЦИЯ СУММЫ
# ========================================

def validate_amount(amount: float, min_amount: float, max_amount: float) -> Tuple[bool, str]:
    """
    Проверяет, что сумма находится в допустимом диапазоне.
    
    Args:
        amount: Сумма для проверки
        min_amount: Минимальная допустимая сумма
        max_amount: Максимальная допустимая сумма
        
    Returns:
        (True, message) если сумма в диапазоне
        (False, message) если сумма вне диапазона
    """
    if amount < min_amount:
        return False, f"Amount {amount} is below minimum {min_amount}"
    
    if amount > max_amount:
        return False, f"Amount {amount} exceeds maximum {max_amount}"
    
    return True, f"Amount {amount} is within valid range"


def check_large_amount_warning(amount: float, max_amount: float, threshold_percent: float = 0.8) -> Tuple[bool, str]:
    """
    Проверяет, не является ли сумма подозрительно большой.
    
    Args:
        amount: Сумма для проверки
        max_amount: Максимальная допустимая сумма
        threshold_percent: Процент от максимума для предупреждения (по умолчанию 80%)
        
    Returns:
        (True, message) если сумма подозрительно большая
        (False, message) если сумма нормальная
    """
    warning_threshold = max_amount * threshold_percent
    
    if amount >= warning_threshold:
        percent = (amount / max_amount) * 100
        return True, f"Amount {amount} is {percent:.1f}% of maximum allowed"
    
    return False, "Amount is not unusually large"


# ========================================
# ВАЛИДАЦИЯ ОБЯЗАТЕЛЬНЫХ ПОЛЕЙ
# ========================================

def validate_required_fields(document: dict, required_fields: List[str]) -> Tuple[bool, str]:
    """
    Проверяет наличие всех обязательных полей в документе.
    
    Args:
        document: Словарь с данными документа
        required_fields: Список обязательных полей
        
    Returns:
        (True, message) если все поля присутствуют
        (False, message) если какие-то поля отсутствуют
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in document or document[field] is None or document[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, "All required fields are present"


# ========================================
# ВАЛИДАЦИЯ ТИПА ДОКУМЕНТА
# ========================================

def validate_document_type(doc_type: str, allowed_types: List[str], blacklisted_types: List[str]) -> Tuple[bool, str]:
    """
    Проверяет, что тип документа разрешен и не находится в черном списке.
    
    Args:
        doc_type: Тип документа
        allowed_types: Список разрешенных типов
        blacklisted_types: Список запрещенных типов
        
    Returns:
        (True, message) если тип документа разрешен
        (False, message) если тип документа не разрешен или в черном списке
    """
    if not doc_type:
        return False, "Document type is empty"
    
    # Проверка черного списка (приоритетнее)
    if doc_type in blacklisted_types:
        return False, f"Document type '{doc_type}' is blacklisted"
    
    # Проверка белого списка
    if doc_type not in allowed_types:
        return False, f"Document type '{doc_type}' is not allowed. Allowed types: {', '.join(allowed_types)}"
    
    return True, f"Document type '{doc_type}' is valid"
