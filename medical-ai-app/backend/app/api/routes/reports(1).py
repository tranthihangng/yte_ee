from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.report import ReportGenerateRequest
from app.services.case_service import CaseService
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = ReportService.get_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo")
    case = CaseService.get_case(db, report.case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy ca bệnh")
    return ReportService.serialize_report(case, report)


@router.post("/{case_id}/generate-pdf")
def generate_pdf(case_id: int, payload: ReportGenerateRequest, db: Session = Depends(get_db)):
    case = CaseService.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy ca bệnh")
    report = ReportService.create_report_record(db, case, payload)
    report = ReportService.generate_pdf(db, case, report)
    return ReportService.serialize_report(case, report)


@router.get("/{case_id}/download-pdf")
def download_pdf(case_id: int, db: Session = Depends(get_db)):
    report = ReportService.get_latest_report_by_case(db, case_id)
    if report is None or not report.pdf_path:
        raise HTTPException(status_code=404, detail="Báo cáo PDF chưa được tạo")
    absolute = settings.backend_dir / report.pdf_path.lstrip("/")
    return FileResponse(str(absolute), media_type="application/pdf", filename=absolute.name)


@router.get("/case/{case_id}/latest")
def get_latest_report_for_case(case_id: int, db: Session = Depends(get_db)):
    case = CaseService.get_case(db, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy ca bệnh")
    report = ReportService.get_latest_report_by_case(db, case_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Ca bệnh chưa có báo cáo")
    return ReportService.serialize_report(case, report)


@router.post("/{report_id}/send-email")
def send_report_email(report_id: int, payload: dict, db: Session = Depends(get_db)):
    report = ReportService.get_report(db, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy báo cáo")
    return {
        "success": True,
        "message": "API gửi email đã sẵn sàng để nối SMTP / Mail service.",
        "report_id": report_id,
        "to": payload.get("to"),
    }
