from __future__ import annotations

import io
import json
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Case, PredictionResult, Report
from app.schemas.report import ReportGenerateRequest
from app.services.storage_service import StorageService


class ReportService:
    @staticmethod
    def get_latest_prediction(case: Case) -> PredictionResult | None:
        if not case.prediction_results:
            return None
        return sorted(case.prediction_results, key=lambda row: row.created_at)[-1]

    @staticmethod
    def create_report_record(db: Session, case: Case, options: ReportGenerateRequest) -> Report:
        report = Report(
            case_id=case.id,
            template_type=options.template_type,
            include_images=options.include_images,
            include_metrics=options.include_metrics,
            include_notes=options.include_notes,
            mask_personal_info=options.mask_personal_info,
            pdf_path="",
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def generate_pdf(db: Session, case: Case, report: Report) -> Report:
        prediction = ReportService.get_latest_prediction(case)
        pdf_path = settings.reports_dir / f"report_case_{case.id}_report_{report.id}.pdf"

        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        margin = 40

        def line(text: str, x: float, y: float, size: int = 11, bold: bool = False):
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(x, y, text)

        c.setTitle("Báo cáo phân tích ảnh y tế")
        line(settings.default_system_name, margin, height - 42, 18, True)
        line("BÁO CÁO PHÂN TÍCH ẢNH Y TẾ", margin + 120, height - 86, 20, True)

        y = height - 130
        c.setLineWidth(1)
        c.line(margin, y, width - margin, y)
        y -= 30

        patient_name = "******" if report.mask_personal_info else case.patient_name
        patient_identifier = "******" if report.mask_personal_info else case.patient_identifier

        info_rows = [
            ("Mã ca", case.case_code),
            ("Bệnh nhân / ID", f"{patient_name} / {patient_identifier}"),
            ("Ngày chụp", str(case.study_date or "")),
            ("Loại phân tích", case.module_type.value.replace("_", " ").title()),
        ]
        for label, value in info_rows:
            line(f"{label}:", margin, y, 12, True)
            line(str(value), margin + 140, y, 12)
            y -= 22

        if prediction and report.include_images:
            artifacts = json.loads(prediction.artifacts_json or "{}")
            original = artifacts.get("original_image")
            result_img = (
                artifacts.get("overlay_image")
                or artifacts.get("gradcam_image")
                or artifacts.get("detection_image")
                or artifacts.get("mask_image")
            )
            box_w, box_h = 180, 180
            y -= 6
            line("Ảnh gốc", margin + 40, y, 12, True)
            line("Ảnh kết quả phân tích", margin + 280, y, 12, True)
            y -= 190
            if original:
                c.drawImage(ImageReader(str(settings.backend_dir / original.lstrip("/"))), margin, y, width=box_w, height=box_h, preserveAspectRatio=True, anchor='c')
            if result_img:
                c.drawImage(ImageReader(str(settings.backend_dir / result_img.lstrip("/"))), margin + 240, y, width=box_w, height=box_h, preserveAspectRatio=True, anchor='c')
            y -= 24

        if prediction:
            line("Kết quả phân tích", margin, y, 14, True)
            y -= 24
            line(f"Phát hiện tổn thương: {prediction.predicted_label}", margin, y, 11)
            y -= 18
            line(f"Độ tin cậy mô hình: {round(prediction.confidence * 100, 1)}%", margin, y, 11)
            y -= 18
            line(f"Tóm tắt: {prediction.summary}", margin, y, 11)
            y -= 18
            if report.include_metrics:
                metrics = json.loads(prediction.metrics_json or "{}")
                for key, value in metrics.items():
                    line(f"{key}: {value}", margin + 18, y, 10)
                    y -= 16

        if report.include_notes and case.notes:
            y -= 10
            line("Ghi chú lâm sàng", margin, y, 14, True)
            y -= 20
            note = case.notes[:300]
            for chunk in [note[i:i + 100] for i in range(0, len(note), 100)]:
                line(chunk, margin, y, 10)
                y -= 14

        y = 80
        c.line(margin, y + 36, width - margin, y + 36)
        line("Bác sĩ xác nhận", margin, y + 14, 11, True)
        line("Hệ thống AI", margin + 220, y + 14, 11, True)
        line("Ngày tạo báo cáo", margin + 390, y + 14, 11, True)
        line(settings.report_signature_name, margin, y - 8, 10)
        line(f"{settings.default_system_name} v{settings.app_version}", margin + 220, y - 8, 10)
        line(report.created_at.strftime("%d/%m/%Y %H:%M:%S"), margin + 390, y - 8, 10)

        c.save()

        report.pdf_path = StorageService.absolute_to_public(pdf_path)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_report(db: Session, report_id: int) -> Report | None:
        return db.get(Report, report_id)

    @staticmethod
    def get_latest_report_by_case(db: Session, case_id: int) -> Report | None:
        stmt = select(Report).where(Report.case_id == case_id).order_by(Report.created_at.desc()).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def serialize_report(case: Case, report: Report) -> dict:
        prediction = ReportService.get_latest_prediction(case)
        pred_data = None
        if prediction:
            pred_data = {
                "predicted_label": prediction.predicted_label,
                "confidence": prediction.confidence,
                "summary": prediction.summary,
                "metrics": json.loads(prediction.metrics_json or "{}"),
                "artifacts": json.loads(prediction.artifacts_json or "{}"),
                "created_at": prediction.created_at.isoformat(),
            }
        return {
            "report": {
                "id": report.id,
                "case_id": report.case_id,
                "template_type": report.template_type,
                "include_images": report.include_images,
                "include_metrics": report.include_metrics,
                "include_notes": report.include_notes,
                "mask_personal_info": report.mask_personal_info,
                "pdf_path": report.pdf_path,
                "created_at": report.created_at.isoformat(),
            },
            "case": {
                "id": case.id,
                "case_code": case.case_code,
                "patient_name": case.patient_name,
                "patient_identifier": case.patient_identifier,
                "study_date": str(case.study_date or ""),
                "module_type": case.module_type.value,
                "status": case.status.value,
                "notes": case.notes,
                "input_file_path": case.input_file_path,
            },
            "prediction": pred_data,
        }
