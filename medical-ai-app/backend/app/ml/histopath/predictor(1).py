from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.services.storage_service import StorageService
from app.ml.histopath.preprocess import preprocess
from app.ml.histopath.postprocess import postprocess
from app.utils.image_utils import save_rgb_image


class HistopathPredictor:
    def __init__(self) -> None:
        self.model = self.load_model()

    def load_model(self):
        """
        Gắn model phân loại mô bệnh học thật của bạn ở đây.
        Hàm chỉ cần trả về model đã load sẵn.
        """
        return {"name": "histopath-stub"}

    def predict(self, file_path: str, confidence_threshold: float = 0.5) -> dict:
        image = preprocess(file_path)
        gradcam = postprocess(image)

        stem = Path(file_path).stem
        original_path = settings.gradcam_dir / f"{stem}_hist_original.png"
        gradcam_path = settings.gradcam_dir / f"{stem}_hist_gradcam.png"

        save_rgb_image(image, original_path)
        save_rgb_image(gradcam, gradcam_path)

        return {
            "module": "histopath",
            "predicted_label": "Lung adenocarcinoma",
            "confidence": max(0.76, confidence_threshold + 0.15),
            "metrics": {
                "top1": "Lung adenocarcinoma",
                "top2": "Benign",
                "top3": "Normal",
            },
            "artifacts": {
                "original_image": StorageService.absolute_to_public(original_path),
                "gradcam_image": StorageService.absolute_to_public(gradcam_path),
            },
            "summary": "Mô hình nghiêng về lớp ung thư biểu mô tuyến phổi",
        }
