from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import CaseStatus, ModuleType
from app.schemas.case import CaseCreate, CaseListResponse, CaseRead, DraftCreate
from app.services.case_service import CaseService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/cases", tags=["cases"])

ALLOWED_EXTENSIONS = {
    "brain_mri": {".png", ".jpg", ".jpeg", ".nii", ".gz", ".dcm"},
    "histopath": {".png", ".jpg", ".jpeg"},
    "wrist_xray": {".png", ".jpg", ".jpeg", ".dcm"},
}


def validate_upload_for_module(filename: str, module_type: str) -> None:
    ext = "".join(Path(filename).suffixes[-2:]).lower() if filename.lower().endswith(".nii.gz") else Path(filename).suffix.lower()
    allowed = ALLOWED_EXTENSIONS.get(module_type, set())
    if ext not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng {ext} không hợp lệ cho mô-đun {module_type}. Cho phép: {', '.join(sorted(allowed))}",
        )


@router.post("", response_model=CaseRead)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    case = CaseService.create_case(db, payload)
    return CaseService.serialize_case(case)


@router.get("", response_model=CaseListResponse)
def list_cases(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=8, ge=1, le=100),
    search: str | None = Query(default=None),
    module_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    items, total = CaseService.list_cases(
        db,
        page=page,
        page_size=page_size,
        search=search,
        module_type=module_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/export-csv")
def export_cases_csv(
    search: str | None = Query(default=None),
    module_type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    content = CaseService.export_cases_csv(
        db,
        search=search,
        module_type=module_type,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="medical_cases.csv"'},
    )


@router.post("/upload")
def upload_file(
    module_type: str,
    file: UploadFile = File(...),
):
    validate_upload_for_module(file.filename or "", module_type)
    absolute_path, preview_path = StorageService.save_upload(file, module_type)
    return {"file_path": absolute_path, "preview_path": preview_path, "filename": file.filename}


@router.post("/drafts")
def save_draft(payload: DraftCreate, db: Session = Depends(get_db)):
    draft = CaseService.save_draft(db, payload)
    return CaseService.serialize_draft(draft)


@router.get("/drafts/latest")
def get_latest_draft(db: Session = Depends(get_db)):
    draft = CaseService.get_latest_draft(db)
    if not draft:
        return {"draft": None}
    return {"draft": CaseService.serialize_draft(draft)}


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = CaseService.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy ca bệnh")
    return CaseService.serialize_case(case)
