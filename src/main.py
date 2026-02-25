from batch_validation import render_batch_validation_page
from logic import check_rules

# В разделе Batch Validation:
render_batch_validation_page(check_rules)
"""
Streamlit интерфейс для системы валидации документов.
Позволяет интерактивно тестировать правила валидации.
"""

import streamlit as st
from datetime import datetime, timedelta
from mock_data import default_document, all_test_cases
from logic import check_rules, get_validation_summary, load_rules

# ========================================
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ========================================

st.set_page_config(
    page_title="Document Flow Bot",
    page_icon=":page_facing_up:",
    layout="wide"
)

# ========================================
# ЗАГОЛОВОК
# ========================================

st.title(":page_facing_up: Document Flow Bot - Rule-Based Validation System")
st.markdown("---")

# ========================================
# SIDEBAR: РЕЖИМ РАБОТЫ
# ========================================

st.sidebar.header("Configuration")

mode = st.sidebar.radio(
    "Select Mode:",
    ["Custom Input", "Test Predefined Cases", "Batch Validation"]
)

st.sidebar.markdown("---")

# ========================================
# РЕЖИМ 1: CUSTOM INPUT
# ========================================

if mode == "Custom Input":
    st.header("1. Document Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Information")
        
        # Тип документа
        document_type = st.selectbox(
            "Document Type",
            ["invoice", "contract", "act", "receipt"],
            index=0,
            help="Select the type of document"
        )
        
        # Номер документа
        document_number = st.text_input(
            "Document Number",
            value=default_document.get("document_number", ""),
            help="Unique document identifier"
        )
        
        # Дата выдачи
        issue_date = st.date_input(
            "Issue Date",
            value=datetime.now(),
            help="Date when document was issued"
        )
        
        # Срок действия (не для всех типов)
        if document_type in ["contract", "invoice"]:
            expiry_date = st.date_input(
                "Expiry Date",
                value=datetime.now() + timedelta(days=45),
                help="Date when document expires"
            )
        else:
            expiry_date = None
    
    with col2:
        st.subheader("Financial & Legal")
        
        # Сумма
        total_amount = st.number_input(
            "Total Amount (RUB)",
            min_value=0.0,
            value=float(default_document.get("total_amount", 0)),
            step=1000.0,
            help="Total amount in rubles"
        )
        
        # ИНН
        inn = st.text_input(
            "INN (Tax ID)",
            value=default_document.get("inn", ""),
            help="10 digits for legal entity, 12 for individual"
        )
        
        # Подпись
        is_signed = st.checkbox(
            "Document is Signed",
            value=default_document.get("is_signed", True),
            help="Whether document has valid signature"
        )
    
    st.markdown("---")
    
    # ========================================
    # КНОПКА ВАЛИДАЦИИ
    # ========================================
    
    if st.button(":mag: Validate Document", type="primary", use_container_width=True):
        
        # Формируем объект документа
        current_document = {
            "document_type": document_type,
            "document_number": document_number,
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "total_amount": total_amount,
            "inn": inn,
            "is_signed": is_signed
        }
        
        # Добавляем expiry_date если есть
        if expiry_date:
            current_document["expiry_date"] = expiry_date.strftime("%Y-%m-%d")
        
        # Добавляем required_fields из правил
        rules = load_rules()
        current_document["required_fields"] = rules['required_fields'].get(document_type, [])
        
        # Запускаем валидацию
        st.header("2. Validation Results")
        
        # Получаем вердикт
        result = check_rules(current_document)
        
        # Отображаем результат с правильным цветом
        if "[ERROR]" in result:
            st.error(result)
        elif "[WARNING]" in result:
            st.warning(result)
        elif "[OK]" in result:
            st.success(result)
        else:
            st.info(result)
        
        # Показываем детальную информацию
        st.markdown("---")
        st.subheader("Detailed Validation Report")
        
        summary = get_validation_summary(current_document)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Document Type", summary['document_type'])
        with col2:
            st.metric("Document Number", summary['document_number'])
        with col3:
            status_color = ":white_check_mark:" if summary['overall_status'] == 'PASS' else ":x:"
            st.metric("Overall Status", f"{status_color} {summary['overall_status']}")
        
        st.markdown("### Individual Checks")
        
        for check_name, check_result in summary['checks'].items():
            status_icon = ":white_check_mark:" if check_result['status'] == 'PASS' else ":x:"
            st.write(f"{status_icon} **{check_name}**: {check_result['message']}")
        
        # Показываем исходный JSON документа
        with st.expander("View Document JSON"):
            st.json(current_document)

# ========================================
# РЕЖИМ 2: TEST PREDEFINED CASES
# ========================================

elif mode == "Test Predefined Cases":
    st.header("Predefined Test Cases")
    st.write("Test the validation system with pre-configured scenarios")
    
    # Выбор категории тестов
    test_category = st.radio(
        "Select Test Category:",
        ["Valid Documents", "Error Cases", "Warning Cases"],
        horizontal=True
    )
    
    # Маппинг категорий
    category_map = {
        "Valid Documents": "valid",
        "Error Cases": "errors",
        "Warning Cases": "warnings"
    }
    
    selected_category = category_map[test_category]
    test_cases = all_test_cases[selected_category]
    
    st.markdown("---")
    
    # Отображаем тесты
    for test_name, test_document in test_cases:
        with st.expander(f":page_facing_up: {test_name}"):
            
            # Показываем документ
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.json(test_document)
            
            with col2:
                if st.button(f"Run Test", key=f"test_{test_name}"):
                    result = check_rules(test_document)
                    
                    if "[ERROR]" in result:
                        st.error(result)
                    elif "[WARNING]" in result:
                        st.warning(result)
                    elif "[OK]" in result:
                        st.success(result)

# ========================================
# РЕЖИМ 3: BATCH VALIDATION
# ========================================

elif mode == "Batch Validation":
    st.header("Batch Validation")
    st.write("Upload multiple documents for batch processing")
    
    st.info(":construction: This feature will be implemented in future versions")
    
    # Placeholder для будущего функционала
    st.markdown("""
    **Planned features:**
    - Upload CSV/Excel with multiple documents
    - Batch validation with summary report
    - Export results to Excel
    - Statistical analysis of validation results
    """)

# ========================================
# FOOTER: СИСТЕМА ПРАВИЛ
# ========================================

st.sidebar.markdown("---")
st.sidebar.header("System Information")

if st.sidebar.checkbox("Show Current Rules"):
    rules = load_rules()
    st.sidebar.json(rules)

st.sidebar.markdown("---")
st.sidebar.info("""
**Document Flow Bot v1.0**

Rule-Based Validation System

Developed for PRIS Lab 2
""")
