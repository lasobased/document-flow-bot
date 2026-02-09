"""
Models - Объектная модель системы документооборота (OOP).
Лабораторная работа №3: Переход от словарей к классам.

Сущности:
- Document: Документ
- Employee: Сотрудник
- Department: Отдел
- DocumentType: Тип документа
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


# ========================================
# ОСНОВНЫЕ СУЩНОСТИ (ENTITIES)
# ========================================

@dataclass
class Department:
    """
    Отдел организации.
    
    Атрибуты:
        name: Название отдела (уникальный идентификатор)
        head_name: ФИО руководителя
        level: Уровень в иерархии (0 - топ-менеджмент)
        can_sign_types: Типы документов, которые может подписывать
    """
    name: str
    head_name: str
    level: int = 1
    can_sign_types: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.name} (Руководитель: {self.head_name})"
    
    def can_sign(self, doc_type: str) -> bool:
        """Проверяет, может ли отдел подписывать данный тип документа"""
        return doc_type in self.can_sign_types or not self.can_sign_types


@dataclass
class Employee:
    """
    Сотрудник организации.
    
    Атрибуты:
        name: ФИО сотрудника
        department: Отдел, в котором работает
        position: Должность
        can_sign: Имеет ли право подписи
        max_sign_amount: Максимальная сумма для подписи (если имеет право)
    """
    name: str
    department: str  # Название отдела
    position: str
    can_sign: bool = False
    max_sign_amount: float = 0.0
    
    def __str__(self):
        return f"{self.name} ({self.position}, {self.department})"
    
    def can_sign_document(self, amount: float) -> bool:
        """Проверяет, может ли сотрудник подписать документ на данную сумму"""
        if not self.can_sign:
            return False
        if self.max_sign_amount == 0:  # Безлимитное право
            return True
        return amount <= self.max_sign_amount


@dataclass
class DocumentType:
    """
    Тип документа.
    
    Атрибуты:
        name: Название типа (invoice, contract, act, receipt)
        description: Описание типа
        required_signatures: Количество необходимых подписей
        approval_chain: Список отделов, через которые должен пройти документ
    """
    name: str
    description: str
    required_signatures: int = 1
    approval_chain: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.name}: {self.description}"


@dataclass
class Document:
    """
    Документ в системе документооборота.
    
    Атрибуты:
        document_number: Уникальный номер документа
        document_type: Тип документа
        author: Автор документа (ФИО)
        department: Отдел-автор
        issue_date: Дата создания
        total_amount: Сумма по документу
        signed_by: Список подписавших (ФИО)
        current_status: Текущий статус (draft, pending, approved, rejected)
    """
    document_number: str
    document_type: str
    author: str
    department: str
    issue_date: str
    total_amount: float = 0.0
    signed_by: List[str] = field(default_factory=list)
    current_status: str = "draft"
    expiry_date: Optional[str] = None
    inn: Optional[str] = None
    
    def __str__(self):
        return f"Документ {self.document_number} ({self.document_type}, {self.current_status})"
    
    def add_signature(self, employee_name: str):
        """Добавляет подпись сотрудника"""
        if employee_name not in self.signed_by:
            self.signed_by.append(employee_name)
    
    def is_fully_signed(self, required_count: int) -> bool:
        """Проверяет, достаточно ли подписей"""
        return len(self.signed_by) >= required_count
    
    def to_dict(self) -> dict:
        """Преобразует объект в словарь для совместимости с логикой валидации"""
        return {
            'document_number': self.document_number,
            'document_type': self.document_type,
            'issue_date': self.issue_date,
            'expiry_date': self.expiry_date,
            'total_amount': self.total_amount,
            'inn': self.inn,
            'is_signed': len(self.signed_by) > 0,
            'required_fields': []  # Будет заполнено при валидации
        }


# ========================================
# ФАБРИЧНЫЕ ФУНКЦИИ
# ========================================

def create_sample_departments() -> List[Department]:
    """Создает примеры отделов для тестирования"""
    return [
        Department(
            name="Финансовый отдел",
            head_name="Иванова Мария Петровна",
            level=1,
            can_sign_types=["invoice", "receipt"]
        ),
        Department(
            name="Юридический отдел",
            head_name="Петров Сергей Иванович",
            level=1,
            can_sign_types=["contract", "act"]
        ),
        Department(
            name="Отдел закупок",
            head_name="Сидорова Анна Васильевна",
            level=2,
            can_sign_types=["invoice", "contract"]
        ),
        Department(
            name="Генеральная дирекция",
            head_name="Смирнов Александр Николаевич",
            level=0,
            can_sign_types=["invoice", "contract", "act", "receipt"]
        )
    ]


def create_sample_employees() -> List[Employee]:
    """Создает примеры сотрудников для тестирования"""
    return [
        Employee(
            name="Иванова Мария Петровна",
            department="Финансовый отдел",
            position="Начальник финансового отдела",
            can_sign=True,
            max_sign_amount=500000.0
        ),
        Employee(
            name="Петров Сергей Иванович",
            department="Юридический отдел",
            position="Начальник юридического отдела",
            can_sign=True,
            max_sign_amount=1000000.0
        ),
        Employee(
            name="Сидорова Анна Васильевна",
            department="Отдел закупок",
            position="Начальник отдела закупок",
            can_sign=True,
            max_sign_amount=300000.0
        ),
        Employee(
            name="Смирнов Александр Николаевич",
            department="Генеральная дирекция",
            position="Генеральный директор",
            can_sign=True,
            max_sign_amount=0.0  # Без ограничений
        ),
        Employee(
            name="Козлов Дмитрий Андреевич",
            department="Финансовый отдел",
            position="Бухгалтер",
            can_sign=False,
            max_sign_amount=0.0
        ),
        Employee(
            name="Новикова Елена Сергеевна",
            department="Отдел закупок",
            position="Специалист по закупкам",
            can_sign=False,
            max_sign_amount=0.0
        )
    ]


def create_sample_document_types() -> List[DocumentType]:
    """Создает типы документов"""
    return [
        DocumentType(
            name="invoice",
            description="Счет-фактура",
            required_signatures=2,
            approval_chain=["Финансовый отдел", "Генеральная дирекция"]
        ),
        DocumentType(
            name="contract",
            description="Договор",
            required_signatures=3,
            approval_chain=["Юридический отдел", "Отдел закупок", "Генеральная дирекция"]
        ),
        DocumentType(
            name="act",
            description="Акт выполненных работ",
            required_signatures=2,
            approval_chain=["Юридический отдел", "Финансовый отдел"]
        ),
        DocumentType(
            name="receipt",
            description="Квитанция",
            required_signatures=1,
            approval_chain=["Финансовый отдел"]
        )
    ]
