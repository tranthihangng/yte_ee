from datetime import date
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.db_case import Case
from app.schemas.case import CaseListResponse
from app.services.case_service import create_case, list_cases, save_draft
from app.services.storage_service import save_upload
from app.utils.export_utils import export_cases_csv

router = APIRouter(prefix="/cases")


@router.post("")
def create_case_route(
    patient_name: str = Form(...),
    patient_identifier: str = Form(...),
    study_date: date = Form(...),
    module_type: str = Form(...),
    notes: Optional[str] = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    path = save_upload(file, module_type)
    case = create_case(db, patient_name, patient_identifier, study_date, module_type, path, notes)
    return case


@router.get("", response_model=CaseListResponse)
def list_cases_route(
    q: Optional[str] = None,
    module: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    rows, total = list_cases(db, q, module, status, from_date, to_date, page, page_size)
    items = []
    for case, pred in rows:
        item = case.__dict__.copy()
        item["confidence"] = pred.confidence if pred else None
        item["predicted_label"] = pred.predicted_label if pred else None
        items.append(item)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{case_id}")
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = db.get(Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/drafts")
def save_draft_route(case_code: str = Form(...), payload: str = Form(...), db: Session = Depends(get_db)):
    return save_draft(db, case_code, payload)


@router.get("/export-csv")
def export_csv(
    q: Optional[str] = None,
    module: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    rows, _ = list_cases(db, q, module, status, from_date, to_date, 1, 5000)
    values = [
        {
            "case_code": c.case_code,
            "patient_name": c.patient_name,
            "patient_identifier": c.patient_identifier,
            "module_type": c.module_type,
            "study_date": c.study_date.isoformat(),
            "status": c.status,
            "predicted_label": p.predicted_label if p else "",
            "confidence": round(p.confidence, 4) if p else "",
        }
        for c, p in rows
    ]
    target = export_cases_csv(values, settings.output_dir / "cases_export.csv")
    return FileResponse(target, media_type="text/csv", filename=Path(target).name)
