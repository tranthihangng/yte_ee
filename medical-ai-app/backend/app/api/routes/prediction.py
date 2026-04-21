from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.brain_mri import predictor as brain_predictor
from app.ml.histopath import predictor as histo_predictor
from app.ml.tuberculosis_counting import predictor as tb_predictor
from app.ml.wrist_xray import predictor as xray_predictor
from app.schemas.report import ReportCreate
from app.services.case_service import create_case
from app.services.prediction_service import save_prediction
from app.services.report_service import create_report_record
from app.services.storage_service import save_upload

router = APIRouter(prefix="/predict")


def _run_prediction(
    db: Session,
    module_type: str,
    predictor,
    file: UploadFile,
    patient_name: str,
    patient_identifier: str,
    study_date: date,
    confidence_threshold: float,
    save_to_history: bool,
    export_report: bool,
    notes: str | None,
):
    path = save_upload(file, module_type)
    try:
        result = predictor.predict(path, confidence_threshold)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"{module_type} prediction failed: {exc}") from exc
    if save_to_history:
        case = create_case(db, patient_name, patient_identifier, study_date, module_type, path, notes, "Đã lưu")
        save_prediction(db, case, result)
        result["case_id"] = case.id
        if export_report:
            create_report_record(db, case.id, ReportCreate())
    return result


@router.post("/brain-mri")
def predict_brain(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_identifier: str = Form(...),
    study_date: date = Form(...),
    confidence_threshold: float = Form(0.8),
    save_to_history: bool = Form(True),
    export_report: bool = Form(False),
    notes: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    return _run_prediction(
        db,
        "brain_mri",
        brain_predictor,
        file,
        patient_name,
        patient_identifier,
        study_date,
        confidence_threshold,
        save_to_history,
        export_report,
        notes,
    )


@router.post("/histopath")
def predict_histopath(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_identifier: str = Form(...),
    study_date: date = Form(...),
    confidence_threshold: float = Form(0.8),
    save_to_history: bool = Form(True),
    export_report: bool = Form(False),
    notes: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    return _run_prediction(
        db,
        "histopath",
        histo_predictor,
        file,
        patient_name,
        patient_identifier,
        study_date,
        confidence_threshold,
        save_to_history,
        export_report,
        notes,
    )


@router.post("/tuberculosis-counting")
def predict_tuberculosis_counting(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_identifier: str = Form(...),
    study_date: date = Form(...),
    confidence_threshold: float = Form(0.25),
    save_to_history: bool = Form(True),
    export_report: bool = Form(False),
    notes: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    return _run_prediction(
        db,
        "tuberculosis_counting",
        tb_predictor,
        file,
        patient_name,
        patient_identifier,
        study_date,
        confidence_threshold,
        save_to_history,
        export_report,
        notes,
    )


@router.post("/wrist-xray")
def predict_wrist_xray(
    file: UploadFile = File(...),
    patient_name: str = Form(...),
    patient_identifier: str = Form(...),
    study_date: date = Form(...),
    confidence_threshold: float = Form(0.8),
    save_to_history: bool = Form(True),
    export_report: bool = Form(False),
    notes: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    return _run_prediction(
        db,
        "wrist_xray",
        xray_predictor,
        file,
        patient_name,
        patient_identifier,
        study_date,
        confidence_threshold,
        save_to_history,
        export_report,
        notes,
    )
