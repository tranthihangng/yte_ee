from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.db_case import CaseStatus


class PredictionMetrics(BaseModel):
    __root__: dict[str, Any]


class PredictionArtifactSet(BaseModel):
    original_image: str | None = None
    overlay_image: str | None = None
    mask_image: str | None = None
    gradcam_image: str | None = None
    detection_image: str | None = None


class PredictionResponse(BaseModel):
    module: str
    predicted_label: str
    confidence: float
    metrics: dict[str, Any]
    artifacts: dict[str, Any]
    summary: str
    case_id: int | None = None
    case_code: str | None = None
    status: CaseStatus | None = None
    report_id: int | None = None
    created_at: datetime | None = None


class PredictRequestMetadata(BaseModel):
    case_code: str
    patient_name: str = ""
    patient_identifier: str = ""
    study_date: date | None = None
    notes: str = ""
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    save_to_history: bool = True
    export_report: bool = False
