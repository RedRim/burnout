from __future__ import annotations

from datetime import date
from enum import IntEnum
from typing import Optional

from sqlalchemy import Column, Integer, UniqueConstraint
from sqlmodel import Field

from app.database import DomainModel


class KPIMonth(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    @classmethod
    def from_name(cls, name: str) -> "KPIMonth":
        normalized = name.strip().lower()
        mapping = {
            "январь": cls.JANUARY,
            "февраль": cls.FEBRUARY,
            "март": cls.MARCH,
            "апрель": cls.APRIL,
            "май": cls.MAY,
            "июнь": cls.JUNE,
            "июль": cls.JULY,
            "август": cls.AUGUST,
            "сентябрь": cls.SEPTEMBER,
            "октябрь": cls.OCTOBER,
            "ноябрь": cls.NOVEMBER,
            "декабрь": cls.DECEMBER,
        }
        if normalized not in mapping:
            raise ValueError(f"Неизвестное название месяца: {name}")
        return mapping[normalized]


class Employee(DomainModel, table=True):
    """
    Таблица с основной информацией о сотрудниках.
    """

    __tablename__ = "employees"

    full_name: str = Field(max_length=255, nullable=False, index=True, description="Полное имя сотрудника")
    tenure_years: float = Field(nullable=False, description="Стаж сотрудника в годах (float)")
    age: Optional[int] = Field(default=None, description="Возраст сотрудника")
    has_subordinates: bool = Field(default=False, nullable=False, description="Есть ли сотрудники в подчинении")
    last_vacation_date: Optional[date] = Field(default=None, description="Дата последнего отпуска")
    took_sick_leave_2025: Optional[bool] = Field(default=None, description="Брал ли сотрудник больничный в 2025 году")
    has_disciplinary_action: Optional[bool] = Field(default=None, description="Наличие действующего выговора")
    participates_in_corporate_events: Optional[bool] = Field(
        default=None,
        description="Участвует ли сотрудник в корпоративных активностях",
    )

class EmployeeKPI(DomainModel, table=True):
    """
    Таблица со значениями выполнения KPI по месяцам.
    """

    __tablename__ = "employee_kpis"

    employee_id: int = Field(foreign_key="employees.id", nullable=False, index=True)
    month: KPIMonth = Field(
        sa_column=Column(Integer, nullable=False),
        description="Месяц KPI (номер 1-12)",
    )
    year: int = Field(default=2025, nullable=False, description="Год KPI периода (по умолчанию 2025)")
    kpi_value: float = Field(nullable=False, description="Значение выполнения KPI")

    __table_args__ = (UniqueConstraint("employee_id", "month", "year", name="uq_employee_month_year"),)

