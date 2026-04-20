from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.db_case import Case, PredictionResult


def summary(db: Session) -> dict:
    total_cases = db.scalar(select(func.count()).select_from(Case)) or 0
    today_cases = (
        db.scalar(
            select(func.count()).select_from(Case).where(func.date(Case.created_at) == func.date("now"))
        )
        or 0
    )
    avg_acc = db.scalar(select(func.avg(PredictionResult.confidence)).select_from(PredictionResult)) or 0
    return {
        "total_cases": total_cases,
        "today_cases": today_cases,
        "avg_accuracy": round(float(avg_acc) * 100, 1),
        "active_modules": 3,
    }


def recent_cases(db: Session, limit: int = 8):
    rows = (
        db.query(Case, PredictionResult)
        .outerjoin(PredictionResult, PredictionResult.case_id == Case.id)
        .order_by(Case.created_at.desc())
        .limit(limit)
        .all()
    )
    return rows
