from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.db_report import Report
from app.schemas.report import ReportCreate
from app.services.report_service import build_report_preview, create_report_record, render_pdf

router = APIRouter(prefix="/reports")


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/case/{case_id}/preview")
def get_report_preview(case_id: int, db: Session = Depends(get_db)):
    payload = build_report_preview(db, case_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Case not found")
    return payload


@router.post("/{case_id}/generate-pdf")
def generate_pdf(case_id: int, payload: ReportCreate, db: Session = Depends(get_db)):
    report = create_report_record(db, case_id, payload)
    pdf_path = render_pdf(db, report)
    return {"report_id": report.id, "pdf_path": pdf_path}


@router.get("/{case_id}/download-pdf")
def download_pdf(case_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(Report).filter(Report.case_id == case_id).order_by(Report.created_at.desc()).first()
    )
    if not report or not report.pdf_path:
        raise HTTPException(status_code=404, detail="No generated PDF")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"report_{case_id}.pdf")
