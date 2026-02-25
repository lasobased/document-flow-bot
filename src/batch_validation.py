"""
Batch Validation - Пакетная обработка документов из CSV.
Добавить в src/main.py в режим "Batch Validation".
"""

import streamlit as st
import pandas as pd
import io
from datetime import datetime

# Импортируй свои модули:
# from logic import check_rules


# ========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ========================================

def row_to_document(row: pd.Series) -> dict:
    """Преобразует строку CSV в словарь документа."""
    doc_type = str(row.get("document_type", "invoice")).strip()

    required_fields_map = {
        "invoice":  ["document_number", "issue_date", "total_amount", "inn"],
        "contract": ["document_number", "issue_date", "expiry_date", "total_amount", "inn"],
        "act":      ["document_number", "issue_date", "total_amount"],
        "receipt":  ["document_number", "issue_date", "total_amount"],
    }

    return {
        "document_type":   doc_type,
        "document_number": str(row.get("document_number", "")),
        "issue_date":      str(row.get("issue_date", "")),
        "expiry_date":     str(row.get("expiry_date", "")),
        "total_amount":    float(row.get("total_amount", 0)),
        "inn":             str(row.get("inn", "")),
        "is_signed":       str(row.get("is_signed", "True")).strip().lower() in ("true", "1", "yes"),
        "required_fields": required_fields_map.get(doc_type, ["document_number", "issue_date"]),
    }


def get_status_emoji(result: str) -> str:
    if "[ERROR]" in result:
        return "❌"
    elif "[WARNING]" in result:
        return "⚠️"
    return "✅"


def results_to_dataframe(docs: list[dict], results: list[str]) -> pd.DataFrame:
    rows = []
    for doc, result in zip(docs, results):
        rows.append({
            "№":              doc.get("document_number", "—"),
            "Тип":            doc.get("document_type", "—"),
            "Дата выдачи":    doc.get("issue_date", "—"),
            "Сумма":          doc.get("total_amount", 0),
            "Статус":         get_status_emoji(result),
            "Результат":      result,
        })
    return pd.DataFrame(rows)


def generate_sample_csv() -> str:
    """Генерирует пример CSV для скачивания."""
    today = datetime.now().strftime("%Y-%m-%d")
    rows = [
        "document_type,document_number,issue_date,expiry_date,total_amount,inn,is_signed",
        f"invoice,INV-001,{today},2026-12-31,15000.00,7743013902,True",
        f"contract,DOG-002,{today},2026-06-01,500000.00,9876543210,True",
        f"invoice,INV-003,{today},2026-12-31,50000.00,123456,True",       # bad INN
        f"invoice,INV-004,{today},2026-12-31,10000.00,7743013902,False",  # unsigned
        f"draft,DRF-005,{today},2026-12-31,1000.00,7743013902,True",      # blacklisted
    ]
    return "\n".join(rows)


# ========================================
# STREAMLIT СТРАНИЦА
# ========================================

def render_batch_validation_page(check_rules_fn):
    """
    Главная функция страницы. Вызови её в main.py:

        from batch_validation import render_batch_validation_page
        from logic import check_rules
        render_batch_validation_page(check_rules)
    """
    st.header("📦 Batch Validation — Пакетная обработка")
    st.markdown("Загрузи CSV-файл с документами и проверь их все за один раз.")

    # --- Скачать пример CSV ---
    with st.expander("📄 Посмотреть формат / скачать пример CSV"):
        sample = generate_sample_csv()
        st.code(sample, language="csv")
        st.download_button(
            label="⬇️ Скачать пример CSV",
            data=sample,
            file_name="sample_documents.csv",
            mime="text/csv",
        )

    st.divider()

    # --- Загрузка файла ---
    uploaded = st.file_uploader("Загрузи CSV файл", type=["csv"])

    if not uploaded:
        st.info("Жди загрузки файла...")
        return

    # --- Чтение CSV ---
    try:
        df = pd.read_csv(uploaded)
    except Exception as e:
        st.error(f"Ошибка чтения CSV: {e}")
        return

    st.success(f"Файл загружен: {len(df)} документов")
    st.dataframe(df, use_container_width=True)

    st.divider()

    # --- Запуск валидации ---
    if st.button("🚀 Запустить валидацию", type="primary"):
        documents = []
        results = []

        progress = st.progress(0, text="Валидация...")
        total = len(df)

        for i, (_, row) in enumerate(df.iterrows()):
            doc = row_to_document(row)
            result = check_rules_fn(doc)
            documents.append(doc)
            results.append(result)
            progress.progress((i + 1) / total, text=f"Обработано: {i+1}/{total}")

        progress.empty()

        # --- Сводка ---
        errors   = sum(1 for r in results if "[ERROR]"   in r)
        warnings = sum(1 for r in results if "[WARNING]" in r)
        ok       = sum(1 for r in results if "[OK]"      in r)

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Прошли", ok)
        col2.metric("⚠️ Предупреждения", warnings)
        col3.metric("❌ Ошибки", errors)

        st.divider()

        # --- Таблица результатов ---
        result_df = results_to_dataframe(documents, results)
        st.dataframe(result_df, use_container_width=True)

        # --- Скачать результаты ---
        csv_out = result_df.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            label="⬇️ Скачать результаты CSV",
            data=csv_out,
            file_name=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

        # --- Детали по ошибкам ---
        if errors > 0:
            with st.expander(f"🔍 Показать детали ошибок ({errors})"):
                for doc, result in zip(documents, results):
                    if "[ERROR]" in result:
                        st.error(f"**{doc['document_number']}** — {result}")
