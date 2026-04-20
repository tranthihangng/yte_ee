from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import CaseStatus
from app.schemas.case import CaseCreate
from app.schemas.report import ReportGenerateRequest
from app.services.case_service import CaseService
from app.services.prediction_service import PredictionService
from app.services.report_service import ReportService
from app.services.storage_service import StorageService
from app.api.routes.cases import validate_upload_for_module

router = APIRouter(prefix="/predict", tags=["prediction"])


def _predict_with_module(
    db: Session,
    *,
    module_type: str,
    file: UploadFile,
    case_code: str,
    patient_name: str,
    patient_identifier: str,
    study_date: date | None,
    notes: str,
    confidence_threshold: float,
    save_to_history: bool,
    export_report: bool,
):
    validate_upload_for_module(file.filename or "", module_type)
    saved_file_path, _preview = StorageService.save_upload(file, module_type)
    prediction = PredictionService.predict(module_type, saved_file_path, confidence_threshold)

    case = None
    report = None
    if save_to_history:
        case = CaseService.upsert_case(
            db,
            case_code=case_code,
            patient_name=patient_name,
            patient_identifier=patient_identifier,
            study_date=study_date,
            module_type=module_type,
            input_file_path=saved_file_path,
            status=CaseStatus.SAVED,
            notes=notes,
        )
        CaseService.attach_prediction(db, case, prediction)
        if export_report:
            report_opts = ReportGenerateRequest()
            report = ReportService.create_report_record(db, case, report_opts)
            report = ReportService.generate_pdf(db, case, report)

    prediction["case_id"] = case.id if case else None
    prediction["case_code"] = case.case_code if case else case_code
    prediction["status"] = case.status.value if case else None
    prediction["report_id"] = report.id if report else None
    return prediction


@router.post("/brain-mri")
def predict_brain_mri(
    file: UploadFile = File(...),
    case_code: str = Form(...),
    patient_name: str = Form(default=""),
    patient_identifier: str = Form(default=""),
    study_date: date | None = Form(default=None),
    notes: str = Form(default=""),
    confidence_threshold: float = Form(default=0.8),
    save_to_history: bool = Form(default=True),
    export_report: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    return _predict_with_module(
        db,
        module_type="brain_mri",
        file=file,
        case_code=case_code,
        patient_name=patient_name,
        patient_identifier=patient_identifier,
        study_date=study_date,
        notes=notes,
        confidence_threshold=confidence_threshold,
        save_to_history=save_to_history,
        export_report=export_report,
    )


@router.post("/histopath")
def predict_histopath(
    file: UploadFile = File(...),
    case_code: str = Form(...),
    patient_name: str = Form(default=""),
    patient_identifier: str = Form(default=""),
    study_date: date | None = Form(default=None),
    notes: str = Form(default=""),
    confidence_threshold: float = Form(default=0.8),
    save_to_history: bool = Form(default=True),
    export_report: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    return _predict_with_module(
        db,
        module_type="histopath",
        file=file,
        case_code=case_code,
        patient_name=patient_name,
        patient_identifier=patient_identifier,
        study_date=study_date,
        notes=notes,
        confidence_threshold=confidence_threshold,
        save_to_history=save_to_history,
        export_report=export_report,
    )


@router.post("/wrist-xray")
def predict_wrist_xray(
    file: UploadFile = File(...),
    case_code: str = Form(...),
    patient_name: str = Form(default=""),
    patient_identifier: str = Form(default=""),
    study_date: date | None = Form(default=None),
    notes: str = Form(default=""),
    confidence_threshold: float = Form(default=0.8),
    save_to_history: bool = Form(default=True),
    export_report: bool = Form(default=False),
    db: Session = Depends(get_db),
):
    return _predict_with_module(
        db,
        module_type="wrist_xray",
        file=file,
        case_code=case_code,
        patient_name=patient_name,
        patient_identifier=patient_identifier,
        study_date=study_date,
        notes=notes,
        confidence_threshold=confidence_threshold,
        save_to_history=save_to_history,
        export_report=export_report,
    )
