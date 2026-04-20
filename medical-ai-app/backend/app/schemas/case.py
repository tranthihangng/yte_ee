from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel


class CaseCreate(BaseModel):
    patient_name: str
    patient_identifier: str
    study_date: date
    module_type: str
    notes: Optional[str] = None
    save_to_history: bool = True


class CaseResponse(BaseModel):
    id: int
    case_code: str
    patient_name: str
    patient_identifier: str
    study_date: date
    module_type: str
    input_file_path: str
    status: str
    created_at: datetime
    confidence: Optional[float] = None
    predicted_label: Optional[str] = None

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    items: list[CaseResponse]
    total: int
    page: int
    page_size: int


class DraftPayload(BaseModel):
    case_code: str
    payload: dict[str, Any]
