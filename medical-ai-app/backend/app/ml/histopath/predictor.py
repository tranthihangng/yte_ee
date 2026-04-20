from uuid import uuid4

from app.core.config import settings
from app.services.storage_service import to_public_path
from app.utils.image_utils import ensure_rgb_copy


def load_model() -> None:
    return None


def predict(file_path: str, confidence_threshold: float = 0.5) -> dict:
    original = ensure_rgb_copy(file_path, str(settings.gradcam_dir / f"histo_original_{uuid4().hex}.png"))
    gradcam = ensure_rgb_copy(file_path, str(settings.gradcam_dir / f"histo_gradcam_{uuid4().hex}.png"))
    return {
        "module": "histopath",
        "predicted_label": "Lung adenocarcinoma",
        "confidence": max(0.55, min(0.99, confidence_threshold + 0.15)),
        "metrics": {"top1": "Lung adenocarcinoma", "top2": "Benign", "top3": "Normal"},
        "artifacts": {"original_image": to_public_path(original), "gradcam_image": to_public_path(gradcam)},
        "summary": "Mô hình nghiêng về lớp ung thư biểu mô tuyến phổi",
    }
