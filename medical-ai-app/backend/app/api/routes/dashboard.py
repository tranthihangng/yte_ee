from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.dashboard_service import recent_cases, summary

router = APIRouter(prefix="/dashboard")


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    return summary(db)


@router.get("/recent-cases")
def get_recent_cases(db: Session = Depends(get_db)):
    rows = recent_cases(db)
    payload = []
    for case, pred in rows:
        payload.append(
            {
                "id": case.id,
                "case_code": case.case_code,
                "module_type": case.module_type,
                "created_at": case.created_at,
                "predicted_label": pred.predicted_label if pred else "-",
                "status": case.status,
                "confidence": pred.confidence if pred else None,
            }
        )
    return payload
