"""create employee and KPI tables

Revision ID: d3b29e0a3d09
Revises: 
Create Date: 2025-11-15 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "d3b29e0a3d09"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_datetime", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_datetime", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("tenure_years", sa.Float(), nullable=False),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("has_subordinates", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_vacation_date", sa.Date(), nullable=True),
        sa.Column("took_sick_leave_2025", sa.Boolean(), nullable=True),
        sa.Column("has_disciplinary_action", sa.Boolean(), nullable=True),
        sa.Column("participates_in_corporate_events", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employees_full_name", "employees", ["full_name"], unique=False)

    op.create_table(
        "employee_kpis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("created_datetime", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_datetime", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.SmallInteger(), nullable=False),
        sa.Column("year", sa.Integer(), server_default=sa.text("2025"), nullable=False),
        sa.Column("kpi_value", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", "month", "year", name="uq_employee_month_year"),
    )
    op.create_index("ix_employee_kpis_employee_id", "employee_kpis", ["employee_id"], unique=False)
    op.create_index("ix_employee_kpis_month_year", "employee_kpis", ["month", "year"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_employee_kpis_month_year", table_name="employee_kpis")
    op.drop_index("ix_employee_kpis_employee_id", table_name="employee_kpis")
    op.drop_table("employee_kpis")
    op.drop_index("ix_employees_full_name", table_name="employees")
    op.drop_table("employees")

