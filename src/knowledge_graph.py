"""
Knowledge Graph - Граф знаний системы документооборота.
Лабораторная работа №3: Построение связей между объектами.

Узлы (Nodes):
- Сотрудник (Employee)
- Документ (Document)
- Отдел (Department)

Связи (Edges):
- Сотрудник --(работает в)--> Отдел
- Документ --(подписывает)--> Сотрудник
- Документ --(создан в)--> Отдел
- Отдел --(может подписать)--> Тип документа
- Документ --(должен пройти через)--> Отдел
"""

import networkx as nx
from typing import List, Dict, Optional, Tuple
from models import Department, Employee, Document, DocumentType


# ========================================
# СОЗДАНИЕ ГРАФА
# ========================================

def create_document_flow_graph(
    departments: List[Department],
    employees: List[Employee],
    documents: List[Document],
    doc_types: List[DocumentType]
) -> nx.DiGraph:
    """
    Создает направленный граф системы документооборота.
    
    Args:
        departments: Список отделов
        employees: Список сотрудников
        documents: Список документов
        doc_types: Список типов документов
        
    Returns:
        NetworkX DiGraph с узлами и связями
    """
    # Создаем направленный граф (DiGraph - Directed Graph)
    G = nx.DiGraph()
    
    # --- 1. ДОБАВЛЕНИЕ УЗЛОВ ---
    
    # Добавляем отделы
    for dept in departments:
        G.add_node(
            dept.name,
            type="department",
            head=dept.head_name,
            level=dept.level,
            data=dept
        )
    
    # Добавляем сотрудников
    for emp in employees:
        G.add_node(
            emp.name,
            type="employee",
            position=emp.position,
            can_sign=emp.can_sign,
            max_amount=emp.max_sign_amount,
            data=emp
        )
    
    # Добавляем документы
    for doc in documents:
        G.add_node(
            doc.document_number,
            type="document",
            doc_type=doc.document_type,
            status=doc.current_status,
            amount=doc.total_amount,
            data=doc
        )
    
    # Добавляем типы документов
    for dt in doc_types:
        G.add_node(
            f"type_{dt.name}",
            type="document_type",
            description=dt.description,
            required_sigs=dt.required_signatures,
            data=dt
        )
    
    # --- 2. ДОБАВЛЕНИЕ СВЯЗЕЙ ---
    
    # Связь: Сотрудник --(работает в)--> Отдел
    for emp in employees:
        if emp.department in G:
            G.add_edge(
                emp.name,
                emp.department,
                relation="works_in"
            )
    
    # Связь: Документ --(создан в)--> Отдел
    for doc in documents:
        if doc.department in G:
            G.add_edge(
                doc.document_number,
                doc.department,
                relation="created_in"
            )
    
    # Связь: Документ --(подписан)--> Сотрудник
    for doc in documents:
        for signer in doc.signed_by:
            if signer in G:
                G.add_edge(
                    doc.document_number,
                    signer,
                    relation="signed_by"
                )
    
    # Связь: Документ --(принадлежит типу)--> Тип документа
    for doc in documents:
        type_node = f"type_{doc.document_type}"
        if type_node in G:
            G.add_edge(
                doc.document_number,
                type_node,
                relation="is_type"
            )
    
    # Связь: Тип документа --(должен пройти через)--> Отдел
    for dt in doc_types:
        type_node = f"type_{dt.name}"
        for dept_name in dt.approval_chain:
            if dept_name in G:
                G.add_edge(
                    type_node,
                    dept_name,
                    relation="approval_required"
                )
    
    # Связь: Отдел --(может подписать)--> Тип документа
    for dept in departments:
        for doc_type in dept.can_sign_types:
            type_node = f"type_{doc_type}"
            if type_node in G:
                G.add_edge(
                    dept.name,
                    type_node,
                    relation="can_sign"
                )
    
    # Связь: Отдел --(руководит)--> Сотрудник (начальник)
    for dept in departments:
        if dept.head_name in G:
            G.add_edge(
                dept.name,
                dept.head_name,
                relation="managed_by"
            )
    
    return G


# ========================================
# ПОИСКОВЫЕ ФУНКЦИИ (QUERIES)
# ========================================

def find_related_entities(graph: nx.DiGraph, start_node: str) -> List[str]:
    """
    Универсальный поиск: Найти все объекты, связанные с start_node.
    
    Args:
        graph: Граф
        start_node: Узел, от которого ищем связи
        
    Returns:
        Список связанных узлов
    """
    if start_node not in graph:
        return []
    
    # Получаем всех соседей (входящие и исходящие связи)
    predecessors = list(graph.predecessors(start_node))
    successors = list(graph.successors(start_node))
    
    return list(set(predecessors + successors))


def find_approval_chain(graph: nx.DiGraph, document_number: str) -> List[str]:
    """
    Находит цепочку согласования для документа.
    
    Args:
        graph: Граф
        document_number: Номер документа
        
    Returns:
        Список отделов, через которые должен пройти документ
    """
    if document_number not in graph:
        return []
    
    # Находим тип документа
    doc_type_node = None
    for neighbor in graph.successors(document_number):
        if graph.nodes[neighbor]['type'] == 'document_type':
            doc_type_node = neighbor
            break
    
    if not doc_type_node:
        return []
    
    # Находим все отделы, через которые должен пройти этот тип документа
    approval_chain = []
    for dept in graph.successors(doc_type_node):
        if graph.nodes[dept]['type'] == 'department':
            # Проверяем, что это связь "approval_required"
            edge_data = graph.get_edge_data(doc_type_node, dept)
            if edge_data and edge_data.get('relation') == 'approval_required':
                approval_chain.append(dept)
    
    return approval_chain


def find_who_can_sign(graph: nx.DiGraph, document_number: str) -> List[str]:
    """
    Находит сотрудников, которые могут подписать документ.
    
    Args:
        graph: Граф
        document_number: Номер документа
        
    Returns:
        Список ФИО сотрудников, которые могут подписать
    """
    if document_number not in graph:
        return []
    
    # Получаем данные документа
    doc_data = graph.nodes[document_number].get('data')
    if not doc_data:
        return []
    
    amount = doc_data.total_amount
    
    # Находим цепочку согласования
    approval_depts = find_approval_chain(graph, document_number)
    
    # Находим начальников этих отделов, которые могут подписать
    signers = []
    for dept_name in approval_depts:
        # Находим начальника отдела
        for employee in graph.predecessors(dept_name):
            if graph.nodes[employee]['type'] == 'employee':
                emp_data = graph.nodes[employee].get('data')
                if emp_data and emp_data.can_sign_document(amount):
                    signers.append(employee)
    
    return list(set(signers))


def find_documents_by_department(graph: nx.DiGraph, department_name: str) -> List[str]:
    """
    Находит все документы, созданные в отделе.
    
    Args:
        graph: Граф
        department_name: Название отдела
        
    Returns:
        Список номеров документов
    """
    if department_name not in graph:
        return []
    
    documents = []
    for predecessor in graph.predecessors(department_name):
        if graph.nodes[predecessor]['type'] == 'document':
            # Проверяем, что это связь "created_in"
            edge_data = graph.get_edge_data(predecessor, department_name)
            if edge_data and edge_data.get('relation') == 'created_in':
                documents.append(predecessor)
    
    return documents


def find_employees_in_department(graph: nx.DiGraph, department_name: str) -> List[str]:
    """
    Находит всех сотрудников отдела.
    
    Args:
        graph: Граф
        department_name: Название отдела
        
    Returns:
        Список ФИО сотрудников
    """
    if department_name not in graph:
        return []
    
    employees = []
    for predecessor in graph.predecessors(department_name):
        if graph.nodes[predecessor]['type'] == 'employee':
            # Проверяем, что это связь "works_in"
            edge_data = graph.get_edge_data(predecessor, department_name)
            if edge_data and edge_data.get('relation') == 'works_in':
                employees.append(predecessor)
    
    return employees


def find_signature_route(graph: nx.DiGraph, document_number: str) -> Dict:
    """
    Строит полный маршрут подписания документа.
    
    Args:
        graph: Граф
        document_number: Номер документа
        
    Returns:
        Словарь с информацией о маршруте
    """
    if document_number not in graph:
        return {}
    
    # Получаем цепочку согласования
    approval_chain = find_approval_chain(graph, document_number)
    
    # Получаем уже подписавших
    signed_by = []
    for signer in graph.successors(document_number):
        if graph.nodes[signer]['type'] == 'employee':
            edge_data = graph.get_edge_data(document_number, signer)
            if edge_data and edge_data.get('relation') == 'signed_by':
                signed_by.append(signer)
    
    # Получаем тех, кто может подписать
    can_sign = find_who_can_sign(graph, document_number)
    
    # Определяем следующий шаг
    next_signers = [s for s in can_sign if s not in signed_by]
    
    return {
        'document': document_number,
        'approval_chain': approval_chain,
        'already_signed': signed_by,
        'can_sign': can_sign,
        'next_step': next_signers,
        'is_complete': len(signed_by) >= len(approval_chain)
    }


def get_graph_statistics(graph: nx.DiGraph) -> Dict:
    """
    Возвращает статистику по графу.
    
    Args:
        graph: Граф
        
    Returns:
        Словарь со статистикой
    """
    node_types = {}
    for node, data in graph.nodes(data=True):
        node_type = data.get('type', 'unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    return {
        'total_nodes': graph.number_of_nodes(),
        'total_edges': graph.number_of_edges(),
        'node_types': node_types,
        'average_degree': sum(dict(graph.degree()).values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0
    }
