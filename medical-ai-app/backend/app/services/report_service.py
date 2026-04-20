from pathlib import Path
import json

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db_case import Case, PredictionResult
from app.models.db_report import Report
from app.schemas.report import ReportCreate
from app.services.storage_service import to_public_path


_FONT_REG_DONE = False
FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"


def _register_vietnamese_font() -> None:
    global _FONT_REG_DONE, FONT_REGULAR, FONT_BOLD
    if _FONT_REG_DONE:
        return
    candidates = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
        Path("C:/Windows/Fonts/tahoma.ttf"),
    ]
    regular = candidates[0] if candidates[0].exists() else None
    bold = candidates[1] if candidates[1].exists() else None
    if regular:
        pdfmetrics.registerFont(TTFont("VN-Regular", str(regular)))
        FONT_REGULAR = "VN-Regular"
    if bold:
        pdfmetrics.registerFont(TTFont("VN-Bold", str(bold)))
        FONT_BOLD = "VN-Bold"
    _FONT_REG_DONE = True


def create_report_record(db: Session, case_id: int, payload: ReportCreate) -> Report:
    report = Report(case_id=case_id, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def _latest_prediction(db: Session, case_id: int) -> PredictionResult | None:
    return (
        db.query(PredictionResult)
        .filter(PredictionResult.case_id == case_id)
        .order_by(PredictionResult.created_at.desc())
        .first()
    )


def _to_fs_from_public(path_or_none: str | None) -> str | None:
    if not path_or_none:
        return None
    if path_or_none.startswith("/uploads/"):
        return str(settings.upload_dir / path_or_none.split("/")[-1])
    if path_or_none.startswith("/outputs/"):
        parts = path_or_none.strip("/").split("/")
        if len(parts) >= 3:
            return str(settings.output_dir / parts[1] / parts[2])
    p = Path(path_or_none)
    return str(p) if p.exists() else None


def build_report_preview(db: Session, case_id: int) -> dict:
    case = db.get(Case, case_id)
    if not case:
        return {}
    prediction = _latest_prediction(db, case_id)
    artifacts = json.loads(prediction.artifacts_json) if prediction and prediction.artifacts_json else {}
    metrics = json.loads(prediction.metrics_json) if prediction and prediction.metrics_json else {}
    case_input_path = case.input_file_path or ""
    is_npy_input = str(case_input_path).lower().endswith(".npy")
    original_image = artifacts.get("original_image") if is_npy_input else to_public_path(case_input_path)
    result_image = artifacts.get("overlay_image") or artifacts.get("gradcam_image") or artifacts.get("detection_image") or artifacts.get("mask_image")
    return {
        "case": {
            "id": case.id,
            "case_code": case.case_code,
            "patient_name": case.patient_name,
            "patient_identifier": case.patient_identifier,
            "study_date": str(case.study_date),
            "module_type": case.module_type,
            "notes": case.notes,
        },
        "prediction": {
            "predicted_label": prediction.predicted_label if prediction else None,
            "confidence": prediction.confidence if prediction else None,
            "summary": prediction.summary if prediction else None,
            "metrics": metrics,
        },
        "images": {
            "original_image": original_image or artifacts.get("original_image"),
            "result_image": result_image,
            "mask_image": artifacts.get("mask_image"),
        },
    }


def render_pdf(db: Session, report: Report) -> str:
    _register_vietnamese_font()
    preview = build_report_preview(db, report.case_id)
    if not preview:
        raise ValueError(f"Case not found for report case_id={report.case_id}")
    case = preview["case"]
    prediction = preview["prediction"]
    images = preview["images"]
    pdf_path = settings.reports_dir / f"report_{report.id}.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    c.setFont(FONT_BOLD, 17)
    c.drawString(45, height - 40, "MedAI Assist")
    c.setFont(FONT_BOLD, 15)
    c.drawCentredString(width / 2, height - 65, "BAO CAO PHAN TICH ANH Y TE")
    c.setStrokeColor(colors.HexColor("#d1d5db"))
    c.line(40, height - 74, width - 40, height - 74)

    c.setFont(FONT_REGULAR, 10.5)
    c.drawString(45, height - 95, f"Mã ca: {case['case_code']}")
    c.drawString(250, height - 95, f"Bệnh nhân / ID: {case['patient_name']} / {case['patient_identifier']}")
    c.drawString(45, height - 113, f"Ngày chụp: {case['study_date']}")
    c.drawString(250, height - 113, f"Loại phân tích: {case['module_type']}")

    if report.include_images:
        orig_fs = _to_fs_from_public(images.get("original_image"))
        res_fs = _to_fs_from_public(images.get("result_image"))
        if orig_fs:
            c.drawImage(orig_fs, 50, height - 320, width=210, height=180, preserveAspectRatio=True, anchor="c", mask="auto")
        if res_fs:
            c.drawImage(res_fs, 310, height - 320, width=210, height=180, preserveAspectRatio=True, anchor="c", mask="auto")
        c.setFont(FONT_REGULAR, 10)
        c.drawCentredString(155, height - 330, "Ảnh gốc")
        c.drawCentredString(415, height - 330, "Ảnh kết quả phân tích")

    y_box = height - 360
    if report.include_metrics:
        c.setFillColor(colors.HexColor("#f3f8ff"))
        c.roundRect(45, y_box - 95, width - 90, 90, 8, fill=1, stroke=0)
        c.setFillColor(colors.black)
        c.setFont(FONT_BOLD, 11)
        c.drawString(55, y_box - 20, "Kết quả phân tích")
        c.setFont(FONT_REGULAR, 10)
        c.drawString(55, y_box - 38, f"Nhãn: {prediction.get('predicted_label') or '-'}")
        c.drawString(55, y_box - 54, f"Độ tin cậy: {round(prediction.get('confidence') or 0, 3)}")
        c.drawString(55, y_box - 70, f"Tóm tắt: {(prediction.get('summary') or '-')[:90]}")

    if report.include_notes:
        c.setFont(FONT_BOLD, 11)
        c.drawString(45, y_box - 120, "Ghi chú lâm sàng")
        c.setFont(FONT_REGULAR, 10)
        notes = (case.get("notes") or "Không có ghi chú lâm sàng.")
        c.drawString(45, y_box - 136, notes[:120])

    c.setFont(FONT_REGULAR, 9)
    c.drawString(45, 55, "MedAI Assist - Báo cáo AI")
    c.drawRightString(width - 45, 55, f"Report ID: {report.id}")
    c.save()
    report.pdf_path = str(pdf_path)
    db.add(report)
    db.commit()
    db.refresh(report)
    return str(pdf_path)


def to_public_pdf(path: str) -> str:
    return f"/outputs/reports/{Path(path).name}"
