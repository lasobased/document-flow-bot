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

# ========================================
# РАСШИРЕННАЯ АНАЛИТИКА И УТИЛИТЫ
# ========================================

def batch_check_rules(documents: list) -> list[dict]:
    """
    Пакетная валидация списка документов.
    Возвращает список с результатами и метаданными.
    """
    results = []
    for i, doc in enumerate(documents):
        try:
            verdict = check_rules(doc)
            results.append({
                "index": i,
                "document_number": doc.get("document_number", "N/A"),
                "verdict": verdict,
                "status": "ERROR" if "[ERROR]" in verdict else "WARNING" if "[WARNING]" in verdict else "OK",
            })
        except Exception as e:
            results.append({
                "index": i,
                "document_number": doc.get("document_number", "N/A"),
                "verdict": f"[ERROR] Исключение при валидации: {str(e)}",
                "status": "ERROR",
            })
    return results


def get_batch_statistics(batch_results: list[dict]) -> dict:
    """
    Считает статистику по результатам пакетной валидации.
    """
    total = len(batch_results)
    ok      = sum(1 for r in batch_results if r["status"] == "OK")
    warnings = sum(1 for r in batch_results if r["status"] == "WARNING")
    errors  = sum(1 for r in batch_results if r["status"] == "ERROR")

    return {
        "total":        total,
        "ok":           ok,
        "warnings":     warnings,
        "errors":       errors,
        "ok_rate":      round(ok / total * 100, 2) if total else 0,
        "error_rate":   round(errors / total * 100, 2) if total else 0,
    }


def filter_by_status(batch_results: list[dict], status: str) -> list[dict]:
    """
    Фильтрует результаты по статусу: 'OK', 'WARNING', 'ERROR'.
    """
    status = status.upper()
    return [r for r in batch_results if r["status"] == status]


def validate_document_safe(document: dict) -> Tuple[str, dict]:
    """
    Безопасная обёртка над check_rules — никогда не падает.
    Возвращает (verdict, meta).
    """
    meta = {
        "document_number": document.get("document_number", "N/A"),
        "document_type":   document.get("document_type", "unknown"),
        "exception":       None,
    }
    try:
        verdict = check_rules(document)
    except Exception as e:
        verdict = f"[ERROR] Внутренняя ошибка: {str(e)}"
        meta["exception"] = str(e)
    return verdict, meta


def explain_verdict(verdict: str) -> dict:
    """
    Разбирает вердикт на составляющие для UI.
    """
    if "[ERROR]" in verdict:
        level = "error"
        emoji = "❌"
        color = "red"
    elif "[WARNING]" in verdict:
        level = "warning"
        emoji = "⚠️"
        color = "orange"
    else:
        level = "ok"
        emoji = "✅"
        color = "green"

    return {
        "level":   level,
        "emoji":   emoji,
        "color":   color,
        "message": verdict,
        "short":   verdict.split("]", 1)[-1].strip() if "]" in verdict else verdict,
    }


def compare_documents(doc_a: dict, doc_b: dict) -> dict:
    """
    Сравнивает два документа и возвращает diff по ключевым полям.
    """
    fields = ["document_type", "document_number", "issue_date",
              "expiry_date", "total_amount", "inn", "is_signed"]
    diff = {}
    for field in fields:
        val_a = doc_a.get(field)
        val_b = doc_b.get(field)
        if val_a != val_b:
            diff[field] = {"a": val_a, "b": val_b}
    return diff


def get_risk_score(document: dict) -> dict:
    """
    Простая скоринговая модель риска документа (0–100).
    Чем выше — тем рискованнее.
    """
    score = 0
    reasons = []

    if not document.get("is_signed", False):
        score += 40
        reasons.append("Документ не подписан (+40)")

    amount = document.get("total_amount", 0)
    if amount > 1_000_000:
        score += 30
        reasons.append("Сумма > 1 000 000 (+30)")
    elif amount > 500_000:
        score += 15
        reasons.append("Сумма > 500 000 (+15)")

    inn = str(document.get("inn", ""))
    if inn and len(inn) not in (10, 12):
        score += 20
        reasons.append("Некорректный ИНН (+20)")

    doc_type = document.get("document_type", "")
    if doc_type in ("draft", "unknown", ""):
        score += 25
        reasons.append(f"Подозрительный тип документа '{doc_type}' (+25)")

    score = min(score, 100)

    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {"score": score, "level": level, "reasons": reasons}


def enrich_document(document: dict) -> dict:
    """
    Добавляет в документ вычисляемые поля перед валидацией.
    """
    from datetime import datetime

    enriched = document.copy()

    # Добавляем метку времени обработки
    enriched["_processed_at"] = datetime.now().isoformat()

    # Нормализуем тип документа
    enriched["document_type"] = str(document.get("document_type", "")).strip().lower()

    # Нормализуем ИНН — убираем пробелы
    if "inn" in enriched:
        enriched["inn"] = str(enriched["inn"]).strip().replace(" ", "")

    # Приводим сумму к float
    try:
        enriched["total_amount"] = float(document.get("total_amount", 0))
    except (ValueError, TypeError):
        enriched["total_amount"] = 0.0

    # Добавляем риск-скор
    enriched["_risk"] = get_risk_score(enriched)

    return enriched
    
    # Определяем общий статус
    all_passed = all(check['status'] == 'PASS' for check in summary['checks'].values())
    summary['overall_status'] = 'PASS' if all_passed else 'FAIL'
    
    return summary
