from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.db_case import CaseStatus, ModuleType


class CaseBase(BaseModel):
    case_code: str = Field(..., min_length=3, max_length=50)
    patient_name: str = ""
    patient_identifier: str = ""
    study_date: date | None = None
    module_type: ModuleType
    notes: str = ""


class CaseCreate(CaseBase):
    input_file_path: str = ""
    status: CaseStatus = CaseStatus.SAVED


class CaseUpdate(BaseModel):
    patient_name: str | None = None
    patient_identifier: str | None = None
    study_date: date | None = None
    module_type: ModuleType | None = None
    status: CaseStatus | None = None
    notes: str | None = None


class LatestPrediction(BaseModel):
    predicted_label: str | None = None
    confidence: float | None = None
    summary: str | None = None
    metrics: dict[str, Any] = {}
    artifacts: dict[str, Any] = {}
    created_at: datetime | None = None


class CaseRead(CaseBase):
    id: int
    input_file_path: str
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    latest_prediction: LatestPrediction | None = None

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    items: list[CaseRead]
    total: int
    page: int
    page_size: int


class DraftCreate(BaseModel):
    case_id: int | None = None
    module_type: str
    payload: dict[str, Any]


class DraftRead(BaseModel):
    id: int
    case_id: int | None = None
    module_type: str
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime
