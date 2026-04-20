from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportCreate(BaseModel):
    template_type: str = "standard"
    include_images: bool = True
    include_metrics: bool = True
    include_notes: bool = True
    mask_personal_info: bool = False


class ReportResponse(BaseModel):
    id: int
    case_id: int
    template_type: str
    include_images: bool
    include_metrics: bool
    include_notes: bool
    mask_personal_info: bool
    pdf_path: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
