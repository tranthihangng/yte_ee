from typing import Any, Optional

from pydantic import BaseModel


class PredictionArtifacts(BaseModel):
    original_image: str
    overlay_image: Optional[str] = None
    mask_image: Optional[str] = None
    gradcam_image: Optional[str] = None
    detection_image: Optional[str] = None


class PredictionResponse(BaseModel):
    module: str
    predicted_label: str
    confidence: float
    metrics: dict[str, Any]
    artifacts: PredictionArtifacts
    summary: str
    case_id: Optional[int] = None
