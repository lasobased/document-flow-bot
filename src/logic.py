"""
Inference Engine - Ядро продукционной системы.
Реализует машину вывода на основе правил if-then.

Архитектура:
1. Загрузка правил из JSON (Knowledge Base)
2. Применение критических фильтров (Hard Filters)
3. Валидация данных
4. Формирование вердикта
"""

import json
import os
from typing import Dict, Tuple
from document_validators import (
    validate_date_format,
    validate_date_not_past,
    validate_expiry_date,
    check_expiry_warning,
    validate_inn,
    validate_amount,
    check_large_amount_warning,
    validate_required_fields,
    validate_document_type
)

# ========================================
# КОНСТАНТЫ И ПУТИ
# ========================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'rules.json')


# ========================================
# ЗАГРУЗКА БАЗЫ ЗНАНИЙ
# ========================================

def load_rules() -> Dict:
    """
    Загружает правила валидации из JSON файла.
    
    Returns:
        Dict с правилами и настройками системы
        
    Raises:
        FileNotFoundError: Если файл правил не найден
        json.JSONDecodeError: Если JSON некорректен
    """
    try:
        with open(RULES_PATH, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        return rules
    except FileNotFoundError:
        raise FileNotFoundError(f"Rules file not found at: {RULES_PATH}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in rules file: {str(e)}", e.doc, e.pos)


# ========================================
# МАШИНА ВЫВОДА (INFERENCE ENGINE)
# ========================================

def check_rules(document: Dict) -> str:
    """
    Основная функция валидации документа.
    Применяет все правила последовательно и возвращает вердикт.
    
    Порядок проверок:
    1. Critical Filters (останавливают выполнение при ошибке)
    2. Hard Validation (обязательные проверки)
    3. Soft Validation (предупреждения)
    4. Business Logic (специфичные правила)
    
    Args:
        document: Словарь с данными документа
        
    Returns:
        Строковый вердикт с префиксом:
        - [ERROR] - критическая ошибка
        - [WARNING] - предупреждение
        - [OK] - успешная валидация
    """
    
    # Загружаем правила
    rules = load_rules()
    
    # ========================================
    # 1. CRITICAL FILTERS (Жесткие фильтры)
    # ========================================
    
    # Правило 1.1: Документ должен быть подписан
    if rules['critical_rules']['must_be_signed']:
        if not document.get('is_signed', False):
            return rules['validation_messages']['error_not_signed']
    
    # Правило 1.2: Тип документа должен быть разрешен
    doc_type = document.get('document_type', '')
    is_valid, error_msg = validate_document_type(
        doc_type,
        rules['document_types']['allowed'],
        rules['document_types']['blacklisted']
    )
    if not is_valid:
        return rules['validation_messages']['error_invalid_type'] + f" ({error_msg})"
    
    # Правило 1.3: Все обязательные поля должны быть заполнены
    required_fields = rules['required_fields'].get(doc_type, [])
    is_valid, error_msg = validate_required_fields(document, required_fields)
    if not is_valid:
        return rules['validation_messages']['error_missing_fields'] + f" ({error_msg})"
    
    # ========================================
    # 2. HARD VALIDATION (Обязательные проверки)
    # ========================================
    
    # Правило 2.1: Валидация даты выдачи
    issue_date = document.get('issue_date', '')
    is_valid, error_msg = validate_date_format(issue_date)
    if not is_valid:
        return rules['validation_messages']['error_invalid_date'] + f" ({error_msg})"
    
    # Правило 2.2: Валидация срока действия (если есть)
    if 'expiry_date' in document:
        expiry_date = document.get('expiry_date', '')
        
        # Проверка формата
        is_valid, error_msg = validate_date_format(expiry_date)
        if not is_valid:
            return rules['validation_messages']['error_invalid_date'] + f" ({error_msg})"
        
        # Проверка, что срок действия > даты выдачи
        is_valid, error_msg = validate_expiry_date(issue_date, expiry_date)
        if not is_valid:
            return f"[ERROR] {error_msg}"
        
        # Проверка, что документ не просрочен
        if rules['critical_rules']['expiry_date_must_be_future']:
            is_valid, error_msg = validate_date_not_past(expiry_date)
            if not is_valid:
                return rules['validation_messages']['error_expired'] + f" ({error_msg})"
    
    # Правило 2.3: Валидация ИНН (если требуется)
    if rules['critical_rules']['must_have_inn'] and 'inn' in document:
        inn = document.get('inn', '')
        is_valid, error_msg = validate_inn(
            inn,
            rules['inn_validation']['allowed_lengths']
        )
        if not is_valid:
            return rules['validation_messages']['error_invalid_inn'] + f" ({error_msg})"
    
    # Правило 2.4: Валидация суммы
    if 'total_amount' in document:
        amount = document.get('total_amount', 0)
        is_valid, error_msg = validate_amount(
            amount,
            rules['thresholds']['min_amount'],
            rules['thresholds']['max_amount']
        )
        if not is_valid:
            return rules['validation_messages']['error_amount_range'] + f" ({error_msg})"
    
    # ========================================
    # 3. SOFT VALIDATION (Предупреждения)
    # ========================================
    
    warnings = []
    
    # Предупреждение 3.1: Срок истекает скоро
    if 'expiry_date' in document:
        expiry_date = document.get('expiry_date', '')
        has_warning, warning_msg = check_expiry_warning(
            expiry_date,
            rules['thresholds']['expiry_warning_days']
        )
        if has_warning:
            warnings.append(f"{rules['validation_messages']['warning_expiring_soon']} ({warning_msg})")
    
    # Предупреждение 3.2: Подозрительно большая сумма
    if 'total_amount' in document:
        amount = document.get('total_amount', 0)
        has_warning, warning_msg = check_large_amount_warning(
            amount,
            rules['thresholds']['max_amount']
        )
        if has_warning:
            warnings.append(f"{rules['validation_messages']['warning_large_amount']} ({warning_msg})")
    
    # ========================================
    # 4. ФОРМИРОВАНИЕ ИТОГОВОГО ВЕРДИКТА
    # ========================================
    
    # Если есть предупреждения, возвращаем их
    if warnings:
        return "\n".join(warnings)
    
    # Все проверки пройдены успешно
    return rules['validation_messages']['success'] + f" for '{doc_type}' document"


# ========================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
# ========================================

def get_validation_summary(document: Dict) -> Dict:
    """
    Возвращает детальную информацию о валидации документа.
    
    Args:
        document: Словарь с данными документа
        
    Returns:
        Dict с результатами каждой проверки
    """
    rules = load_rules()
    summary = {
        'document_type': document.get('document_type', 'unknown'),
        'document_number': document.get('document_number', 'N/A'),
        'checks': {},
        'overall_status': 'UNKNOWN'
    }
    
    # Проверяем каждое правило и сохраняем результат
    doc_type = document.get('document_type', '')
    
    # Проверка подписи
    summary['checks']['is_signed'] = {
        'status': 'PASS' if document.get('is_signed', False) else 'FAIL',
        'message': 'Document is signed' if document.get('is_signed', False) else 'Document is not signed'
    }
    
    # Проверка типа документа
    is_valid, msg = validate_document_type(
        doc_type,
        rules['document_types']['allowed'],
        rules['document_types']['blacklisted']
    )
    summary['checks']['document_type'] = {
        'status': 'PASS' if is_valid else 'FAIL',
        'message': msg
    }
    
    # Проверка обязательных полей
    required_fields = rules['required_fields'].get(doc_type, [])
    is_valid, msg = validate_required_fields(document, required_fields)
    summary['checks']['required_fields'] = {
        'status': 'PASS' if is_valid else 'FAIL',
        'message': msg
    }
    
    # Проверка даты
    issue_date = document.get('issue_date', '')
    is_valid, msg = validate_date_format(issue_date)
    summary['checks']['issue_date'] = {
        'status': 'PASS' if is_valid else 'FAIL',
        'message': msg
    }
    
    # Проверка ИНН
    if 'inn' in document:
        inn = document.get('inn', '')
        is_valid, msg = validate_inn(inn, rules['inn_validation']['allowed_lengths'])
        summary['checks']['inn'] = {
            'status': 'PASS' if is_valid else 'FAIL',
            'message': msg
        }
    
    # Проверка суммы
    if 'total_amount' in document:
        amount = document.get('total_amount', 0)
        is_valid, msg = validate_amount(
            amount,
            rules['thresholds']['min_amount'],
            rules['thresholds']['max_amount']
        )
        summary['checks']['amount'] = {
            'status': 'PASS' if is_valid else 'FAIL',
            'message': msg
        }
    
    # Определяем общий статус
    all_passed = all(check['status'] == 'PASS' for check in summary['checks'].values())
    summary['overall_status'] = 'PASS' if all_passed else 'FAIL'
    
    return summary
