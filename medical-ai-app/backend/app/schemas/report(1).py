from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ReportOptions(BaseModel):
    template_type: str = "standard"
    include_images: bool = True
    include_metrics: bool = True
    include_notes: bool = True
    mask_personal_info: bool = False
    show_logo: bool = True


class ReportGenerateRequest(ReportOptions):
    pass


class ReportRead(BaseModel):
    id: int
    case_id: int
    template_type: str
    include_images: bool
    include_metrics: bool
    include_notes: bool
    mask_personal_info: bool
    pdf_path: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReportPreviewResponse(BaseModel):
    report: ReportRead
    case: dict[str, Any]
    prediction: dict[str, Any] | None = None
