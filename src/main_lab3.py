"""
Streamlit интерфейс для Лабораторной работы №3: Граф знаний.
Визуализация и анализ связей в системе документооборота.
"""

import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib
from models import (
    create_sample_departments,
    create_sample_employees,
    create_sample_document_types,
    Document
)
from knowledge_graph import (
    create_document_flow_graph,
    find_related_entities,
    find_approval_chain,
    find_who_can_sign,
    find_documents_by_department,
    find_employees_in_department,
    find_signature_route,
    get_graph_statistics
)

# Настройка для корректного отображения русских букв в графах
matplotlib.rcParams['font.family'] = 'DejaVu Sans'

# ========================================
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ========================================

st.set_page_config(
    page_title="Knowledge Graph - Lab 3",
    page_icon="🕸️",
    layout="wide"
)

# ========================================
# ИНИЦИАЛИЗАЦИЯ ДАННЫХ
# ========================================

@st.cache_data
def initialize_data():
    """Инициализирует примеры данных"""
    departments = create_sample_departments()
    employees = create_sample_employees()
    doc_types = create_sample_document_types()
    
    # Создаем примеры документов
    documents = [
        Document(
            document_number="INV-2024-001",
            document_type="invoice",
            author="Козлов Дмитрий Андреевич",
            department="Финансовый отдел",
            issue_date="2024-02-01",
            total_amount=250000.0,
            signed_by=["Иванова Мария Петровна"],
            current_status="pending",
            inn="7743013902"
        ),
        Document(
            document_number="DOG-2024-015",
            document_type="contract",
            author="Новикова Елена Сергеевна",
            department="Отдел закупок",
            issue_date="2024-02-05",
            total_amount=850000.0,
            signed_by=["Петров Сергей Иванович", "Сидорова Анна Васильевна"],
            current_status="pending",
            expiry_date="2025-02-05",
            inn="7707083893"
        ),
        Document(
            document_number="ACT-2024-032",
            document_type="act",
            author="Козлов Дмитрий Андреевич",
            department="Финансовый отдел",
            issue_date="2024-02-08",
            total_amount=120000.0,
            signed_by=[],
            current_status="draft"
        ),
        Document(
            document_number="RCP-2024-099",
            document_type="receipt",
            author="Козлов Дмитрий Андреевич",
            department="Финансовый отдел",
            issue_date="2024-02-09",
            total_amount=15000.0,
            signed_by=["Иванова Мария Петровна"],
            current_status="approved"
        )
    ]
    
    return departments, employees, doc_types, documents

departments, employees, doc_types, documents = initialize_data()

@st.cache_resource
def create_graph():
    """Создает граф знаний"""
    return create_document_flow_graph(departments, employees, documents, doc_types)

G = create_graph()

# ========================================
# ЗАГОЛОВОК
# ========================================

st.title("🕸️ Knowledge Graph Explorer - Лабораторная №3")
st.markdown("### Граф знаний системы документооборота")
st.markdown("---")

# ========================================
# SIDEBAR: СТАТИСТИКА
# ========================================

st.sidebar.header("📊 Статистика графа")
stats = get_graph_statistics(G)

st.sidebar.metric("Всего узлов", stats['total_nodes'])
st.sidebar.metric("Всего связей", stats['total_edges'])
st.sidebar.metric("Средняя степень узла", f"{stats['average_degree']:.2f}")

st.sidebar.markdown("**Типы узлов:**")
for node_type, count in stats['node_types'].items():
    st.sidebar.write(f"- {node_type}: {count}")

st.sidebar.markdown("---")

# ========================================
# РЕЖИМЫ РАБОТЫ
# ========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Поиск связей",
    "📋 Маршрут подписания",
    "📊 Визуализация графа",
    "ℹ️ Информация об узлах"
])

# ========================================
# TAB 1: ПОИСК СВЯЗЕЙ
# ========================================

with tab1:
    st.header("Поиск связанных объектов")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Выбор узла
        all_nodes = list(G.nodes())
        selected_node = st.selectbox(
            "Выберите объект для поиска связей:",
            all_nodes,
            help="Выберите документ, сотрудника или отдел"
        )
    
    with col2:
        # Информация о выбранном узле
        if selected_node:
            node_data = G.nodes[selected_node]
            st.info(f"**Тип:** {node_data.get('type', 'unknown')}")
    
    # Кнопка поиска
    if st.button("🔍 Найти связи", type="primary", use_container_width=True):
        results = find_related_entities(G, selected_node)
        
        if results:
            st.success(f"Найдено связей: {len(results)}")
            
            # Группируем результаты по типам
            results_by_type = {}
            for node in results:
                node_type = G.nodes[node].get('type', 'unknown')
                if node_type not in results_by_type:
                    results_by_type[node_type] = []
                results_by_type[node_type].append(node)
            
            # Отображаем результаты
            for node_type, nodes in results_by_type.items():
                with st.expander(f"📌 {node_type.upper()} ({len(nodes)})"):
                    for node in nodes:
                        # Определяем тип связи
                        edge_in = G.get_edge_data(selected_node, node)
                        edge_out = G.get_edge_data(node, selected_node)
                        
                        relation = "связан с"
                        if edge_in:
                            relation = edge_in.get('relation', 'связан с')
                        elif edge_out:
                            relation = f"← {edge_out.get('relation', 'связан с')}"
                        
                        st.write(f"**{node}** ({relation})")
        else:
            st.warning("Связи не найдены")

# ========================================
# TAB 2: МАРШРУТ ПОДПИСАНИЯ
# ========================================

with tab2:
    st.header("Маршрут подписания документа")
    
    # Выбор документа
    doc_numbers = [doc.document_number for doc in documents]
    selected_doc = st.selectbox(
        "Выберите документ:",
        doc_numbers,
        help="Выберите документ для анализа маршрута"
    )
    
    if st.button("📋 Построить маршрут", type="primary", use_container_width=True):
        route = find_signature_route(G, selected_doc)
        
        if route:
            # Информация о документе
            doc = next((d for d in documents if d.document_number == selected_doc), None)
            if doc:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Тип документа", doc.document_type)
                with col2:
                    st.metric("Сумма", f"{doc.total_amount:,.2f} ₽")
                with col3:
                    status_color = "🟢" if route['is_complete'] else "🟡"
                    st.metric("Статус", f"{status_color} {doc.current_status}")
            
            st.markdown("---")
            
            # Цепочка согласования
            st.subheader("📌 Цепочка согласования")
            if route['approval_chain']:
                for i, dept in enumerate(route['approval_chain'], 1):
                    st.write(f"{i}. **{dept}**")
            else:
                st.info("Цепочка согласования не определена")
            
            st.markdown("---")
            
            # Уже подписали
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✅ Уже подписали")
                if route['already_signed']:
                    for signer in route['already_signed']:
                        emp = next((e for e in employees if e.name == signer), None)
                        if emp:
                            st.success(f"**{signer}**\n\n{emp.position}")
                        else:
                            st.success(signer)
                else:
                    st.info("Документ еще не подписан")
            
            with col2:
                st.subheader("⏳ Могут подписать")
                if route['next_step']:
                    for signer in route['next_step']:
                        emp = next((e for e in employees if e.name == signer), None)
                        if emp:
                            st.warning(f"**{signer}**\n\n{emp.position}")
                        else:
                            st.warning(signer)
                else:
                    if route['is_complete']:
                        st.success("✅ Все подписи собраны!")
                    else:
                        st.info("Нет доступных подписантов")
        else:
            st.error("Не удалось построить маршрут")

# ========================================
# TAB 3: ВИЗУАЛИЗАЦИЯ
# ========================================

with tab3:
    st.header("Визуализация графа знаний")
    
    # Настройки визуализации
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("Настройки")
        
        layout_type = st.selectbox(
            "Тип раскладки:",
            ["spring", "circular", "kamada_kawai", "shell"],
            help="Алгоритм размещения узлов"
        )
        
        show_labels = st.checkbox("Показать подписи", value=True)
        node_size = st.slider("Размер узлов", 100, 3000, 1500)
        
        # Фильтр по типам узлов
        st.markdown("**Показать типы:**")
        show_employees = st.checkbox("Сотрудники", value=True)
        show_departments = st.checkbox("Отделы", value=True)
        show_documents = st.checkbox("Документы", value=True)
        show_doc_types = st.checkbox("Типы документов", value=True)
    
    with col2:
        st.subheader("Граф")
        
        # Создаем подграф с выбранными узлами
        nodes_to_show = []
        for node, data in G.nodes(data=True):
            node_type = data.get('type')
            if (node_type == 'employee' and show_employees) or \
               (node_type == 'department' and show_departments) or \
               (node_type == 'document' and show_documents) or \
               (node_type == 'document_type' and show_doc_types):
                nodes_to_show.append(node)
        
        subgraph = G.subgraph(nodes_to_show)
        
        # Рисуем граф
        fig, ax = plt.subplots(figsize=(14, 10))
        
        # Выбираем раскладку
        if layout_type == "spring":
            pos = nx.spring_layout(subgraph, k=1, iterations=50)
        elif layout_type == "circular":
            pos = nx.circular_layout(subgraph)
        elif layout_type == "kamada_kawai":
            pos = nx.kamada_kawai_layout(subgraph)
        else:
            pos = nx.shell_layout(subgraph)
        
        # Цвета для разных типов узлов
        color_map = {
            'employee': '#FFB6C1',      # Розовый
            'department': '#87CEEB',    # Голубой
            'document': '#90EE90',      # Светло-зеленый
            'document_type': '#FFD700'  # Золотой
        }
        
        node_colors = [
            color_map.get(subgraph.nodes[node].get('type'), '#CCCCCC')
            for node in subgraph.nodes()
        ]
        
        # Рисуем узлы
        nx.draw_networkx_nodes(
            subgraph, pos,
            node_color=node_colors,
            node_size=node_size,
            alpha=0.8,
            ax=ax
        )
        
        # Рисуем ребра
        nx.draw_networkx_edges(
            subgraph, pos,
            edge_color='gray',
            alpha=0.5,
            arrows=True,
            arrowsize=20,
            ax=ax
        )
        
        # Рисуем подписи
        if show_labels:
            # Сокращаем длинные названия
            labels = {}
            for node in subgraph.nodes():
                if len(node) > 20:
                    labels[node] = node[:17] + "..."
                else:
                    labels[node] = node
            
            nx.draw_networkx_labels(
                subgraph, pos,
                labels=labels,
                font_size=8,
                font_weight='bold',
                ax=ax
            )
        
        ax.set_title("Граф знаний системы документооборота", fontsize=16, fontweight='bold')
        ax.axis('off')
        
        st.pyplot(fig)
        
        # Легенда
        st.markdown("**Легенда:**")
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.markdown("🟣 **Сотрудники**")
        with col_b:
            st.markdown("🔵 **Отделы**")
        with col_c:
            st.markdown("🟢 **Документы**")
        with col_d:
            st.markdown("🟡 **Типы документов**")

# ========================================
# TAB 4: ИНФОРМАЦИЯ
# ========================================

with tab4:
    st.header("Информация об узлах графа")
    
    # Группируем по типам
    employees_list = [n for n, d in G.nodes(data=True) if d.get('type') == 'employee']
    departments_list = [n for n, d in G.nodes(data=True) if d.get('type') == 'department']
    documents_list = [n for n, d in G.nodes(data=True) if d.get('type') == 'document']
    doc_types_list = [n for n, d in G.nodes(data=True) if d.get('type') == 'document_type']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Сотрудники
        with st.expander(f"👥 Сотрудники ({len(employees_list)})"):
            for emp_name in employees_list:
                emp = next((e for e in employees if e.name == emp_name), None)
                if emp:
                    st.markdown(f"**{emp.name}**")
                    st.write(f"- Должность: {emp.position}")
                    st.write(f"- Отдел: {emp.department}")
                    st.write(f"- Право подписи: {'✅ Да' if emp.can_sign else '❌ Нет'}")
                    if emp.can_sign:
                        limit = "∞" if emp.max_sign_amount == 0 else f"{emp.max_sign_amount:,.0f} ₽"
                        st.write(f"- Лимит: {limit}")
                    st.markdown("---")
        
        # Отделы
        with st.expander(f"🏢 Отделы ({len(departments_list)})"):
            for dept_name in departments_list:
                dept = next((d for d in departments if d.name == dept_name), None)
                if dept:
                    st.markdown(f"**{dept.name}**")
                    st.write(f"- Руководитель: {dept.head_name}")
                    st.write(f"- Уровень: {dept.level}")
                    st.write(f"- Может подписывать: {', '.join(dept.can_sign_types) if dept.can_sign_types else 'Все типы'}")
                    
                    # Сотрудники отдела
                    dept_employees = find_employees_in_department(G, dept_name)
                    st.write(f"- Сотрудников: {len(dept_employees)}")
                    st.markdown("---")
    
    with col2:
        # Документы
        with st.expander(f"📄 Документы ({len(documents_list)})"):
            for doc_num in documents_list:
                doc = next((d for d in documents if d.document_number == doc_num), None)
                if doc:
                    st.markdown(f"**{doc.document_number}**")
                    st.write(f"- Тип: {doc.document_type}")
                    st.write(f"- Автор: {doc.author}")
                    st.write(f"- Отдел: {doc.department}")
                    st.write(f"- Сумма: {doc.total_amount:,.2f} ₽")
                    st.write(f"- Статус: {doc.current_status}")
                    st.write(f"- Подписей: {len(doc.signed_by)}")
                    st.markdown("---")
        
        # Типы документов
        with st.expander(f"📋 Типы документов ({len(doc_types_list)})"):
            for dt_name in doc_types_list:
                dt = next((d for d in doc_types if f"type_{d.name}" == dt_name), None)
                if dt:
                    st.markdown(f"**{dt.description}**")
                    st.write(f"- Код: {dt.name}")
                    st.write(f"- Требуется подписей: {dt.required_signatures}")
                    st.write(f"- Цепочка: {' → '.join(dt.approval_chain)}")
                    st.markdown("---")

# ========================================
# FOOTER
# ========================================

st.sidebar.markdown("---")
st.sidebar.info("""
**Document Flow Bot**
**Лабораторная работа №3**

Граф знаний системы документооборота

**Узлы:** Сотрудники, Отделы, Документы, Типы

**Связи:** works_in, created_in, signed_by, approval_required, can_sign
""")
