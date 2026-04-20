from datetime import date, datetime
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.core.security import generate_case_code
from app.models.db_case import Case, Draft, PredictionResult


def create_case(
    db: Session,
    patient_name: str,
    patient_identifier: str,
    study_date: date,
    module_type: str,
    input_file_path: str,
    notes: Optional[str] = None,
    status: str = "Chờ xác nhận",
) -> Case:
    record = Case(
        case_code=generate_case_code(),
        patient_name=patient_name,
        patient_identifier=patient_identifier,
        study_date=study_date,
        module_type=module_type,
        input_file_path=input_file_path,
        notes=notes,
        status=status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_cases(
    db: Session,
    q: Optional[str],
    module: Optional[str],
    status: Optional[str],
    from_date: Optional[date],
    to_date: Optional[date],
    page: int,
    page_size: int,
):
    filters = []
    if q:
        filters.append(Case.case_code.ilike(f"%{q}%"))
    if module and module != "all":
        filters.append(Case.module_type == module)
    if status and status != "all":
        filters.append(Case.status == status)
    if from_date:
        filters.append(Case.study_date >= from_date)
    if to_date:
        filters.append(Case.study_date <= to_date)
    where_clause = and_(*filters) if filters else True
    total = db.scalar(select(func.count()).select_from(Case).where(where_clause)) or 0
    rows = (
        db.query(Case, PredictionResult)
        .outerjoin(PredictionResult, PredictionResult.case_id == Case.id)
        .filter(where_clause)
        .order_by(Case.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return rows, total


def save_draft(db: Session, case_code: str, payload_json: str) -> Draft:
    draft = Draft(case_code=case_code, payload_json=payload_json)
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def today_case_count(db: Session) -> int:
    today = datetime.utcnow().date()
    return db.scalar(select(func.count()).select_from(Case).where(Case.study_date == today)) or 0
