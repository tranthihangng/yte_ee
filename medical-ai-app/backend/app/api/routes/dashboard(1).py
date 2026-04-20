from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import RecentCasesResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(search: str | None = Query(default=None), db: Session = Depends(get_db)):
    return DashboardService.get_summary(db, search=search)


@router.get("/recent-cases", response_model=RecentCasesResponse)
def get_recent_cases(limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    return {"items": DashboardService.recent_cases(db, limit=limit)}


@router.get("/notifications")
def get_notifications(limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    return {"items": DashboardService.list_notifications(db, limit=limit)}
