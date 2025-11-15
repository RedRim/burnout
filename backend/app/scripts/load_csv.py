from __future__ import annotations

import argparse
import csv
import logging
import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from sqlmodel import Session, select

from app.database import session_maker, sync_engine
from app.models import Employee, EmployeeKPI, KPIMonth

logger = logging.getLogger(__name__)

MONTH_COLUMN_NAMES: Dict[str, KPIMonth] = {
    "январь": KPIMonth.JANUARY,
    "февраль": KPIMonth.FEBRUARY,
    "март": KPIMonth.MARCH,
    "апрель": KPIMonth.APRIL,
    "май": KPIMonth.MAY,
    "июнь": KPIMonth.JUNE,
    "июль": KPIMonth.JULY,
    "август": KPIMonth.AUGUST,
    "сентябрь": KPIMonth.SEPTEMBER,
    "октябрь": KPIMonth.OCTOBER,
    "ноябрь": KPIMonth.NOVEMBER,
    "декабрь": KPIMonth.DECEMBER,
}

DEFAULT_CSV_PATH = Path(__file__).resolve().parents[2] / "Dannye-dlia-khakatona_no_city.csv"


def normalize_header(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def normalize_value(value: Optional[str]) -> str:
    return (value or "").strip()


def parse_bool(value: str) -> Optional[bool]:
    normalized = value.strip().lower()
    if not normalized or normalized == "нет":
        return False if normalized else None
    if normalized in {"да", "yes", "true", "1"}:
        return True
    if normalized in {"нет", "no", "false", "0"}:
        return False
    return None


def parse_subordinates(value: str) -> bool:
    normalized = value.strip().lower()
    return "руковод" in normalized


def parse_tenure(value: str) -> float:
    text = value.replace("\n", " ").replace(",", " ").strip().lower()
    years = 0.0
    months = 0.0

    year_match = re.search(r"(\d+)\s*(?:лет|год|года)", text)
    if year_match:
        years = float(year_match.group(1))

    month_match = re.search(r"(\d+)\s*месяц", text)
    if month_match:
        months = float(month_match.group(1))

    if not year_match and not month_match and text:
        try:
            years = float(text.replace(",", "."))
        except ValueError as exc:
            raise ValueError(f"Не удалось преобразовать стаж: {value}") from exc

    return years + months / 12


def parse_optional_int(value: str) -> Optional[int]:
    value = value.strip()
    if not value or value.lower() == "нет":
        return None
    return int(float(value))


def parse_optional_date(value: str) -> Optional[date]:
    value = value.strip()
    if not value or value.lower() == "нет":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Не удалось преобразовать дату: {value}")


def parse_kpi_value(value: str) -> Optional[float]:
    value = value.strip()
    if not value or value.lower() == "нет":
        return None
    return float(value.replace(",", "."))


def load_csv_data(
    csv_path: Path,
    kpi_year: int = 2025,
) -> None:
    with csv_path.open("r", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError("CSV файл не содержит заголовок")

        normalized_headers = {normalize_header(name) for name in reader.fieldnames if name}

        required_headers = [
            "фио",
            "стаж",
            "возраст",
            "в подчиненнии сотрудники",
            "отпуск (когда ходил в последний раз)",
            "больничный (брал или нет в 2025 году)",
            "выговор (да/нет)",
            "участие в активностях корпоративных",
        ]
        for header in required_headers:
            if header not in normalized_headers:
                raise KeyError(f"Не найден обязательный столбец '{header}'")

        with Session(sync_engine) as session:
            for raw_row in reader:
                row = {normalize_header(k): normalize_value(v) for k, v in raw_row.items() if k}
                full_name = row.get("фио", "")
                if not full_name:
                    logger.warning("Пропущена строка без ФИО: %s", raw_row)
                    continue

                employee = Employee(
                    full_name=full_name,
                    tenure_years=parse_tenure(row.get("стаж", "")),
                    age=parse_optional_int(row.get("возраст", "")),
                    has_subordinates=parse_subordinates(row.get("в подчиненнии сотрудники", "")),
                    last_vacation_date=parse_optional_date(row.get("отпуск (когда ходил в последний раз)", "")),
                    took_sick_leave_2025=parse_bool(row.get("больничный (брал или нет в 2025 году)", "")),
                    has_disciplinary_action=parse_bool(row.get("выговор (да/нет)", "")),
                    participates_in_corporate_events=parse_bool(row.get("участие в активностях корпоративных", "")),
                )

                existing_employee = session.exec(
                    select(Employee).where(Employee.full_name == employee.full_name)
                ).one_or_none()

                if existing_employee:
                    logger.info("Пропускаю существующего сотрудника %s", employee.full_name)
                    continue

                session.add(employee)
                session.flush()

                for column_name, month_enum in MONTH_COLUMN_NAMES.items():
                    value = row.get(column_name)
                    if value is None:
                        continue
                    kpi_value = parse_kpi_value(value)
                    if kpi_value is None:
                        continue
                    session.add(
                        EmployeeKPI(
                            employee_id=employee.id,
                            month=month_enum,
                            year=kpi_year,
                            kpi_value=kpi_value,
                        )
                    )

            session.commit()


def parse_args(args: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Загрузка данных сотрудников из CSV в базу данных")
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_CSV_PATH,
        help="Путь к CSV-файлу с данными (по умолчанию data из репозитория)",
    )
    parser.add_argument(
        "--kpi-year",
        type=int,
        default=2025,
        help="Значение года для KPI записей (по умолчанию 2025)",
    )
    return parser.parse_args(args)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()
    csv_path = args.file

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV файл не найден: {csv_path}")

    logger.info("Начинаю загрузку данных из %s", csv_path)
    load_csv_data(csv_path=csv_path, kpi_year=args.kpi_year)
    logger.info("Загрузка завершена")


if __name__ == "__main__":
    main()

