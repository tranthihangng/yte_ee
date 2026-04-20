from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.services.storage_service import StorageService
from app.ml.wrist_xray.preprocess import preprocess
from app.ml.wrist_xray.postprocess import postprocess
from app.utils.image_utils import save_rgb_image


class WristXrayPredictor:
    def __init__(self) -> None:
        self.model = self.load_model()

    def load_model(self):
        """
        Gắn model YOLO / detector thật của bạn ở đây.
        """
        return {"name": "wrist-xray-stub"}

    def predict(self, file_path: str, confidence_threshold: float = 0.5) -> dict:
        image = preprocess(file_path)
        detection = postprocess(image)

        stem = Path(file_path).stem
        original_path = settings.detections_dir / f"{stem}_wrist_original.png"
        detection_path = settings.detections_dir / f"{stem}_wrist_detection.png"

        save_rgb_image(image, original_path)
        save_rgb_image(detection, detection_path)

        return {
            "module": "wrist_xray",
            "predicted_label": "Fracture",
            "confidence": max(0.72, confidence_threshold + 0.12),
            "metrics": {
                "detections": 2,
            },
            "artifacts": {
                "original_image": StorageService.absolute_to_public(original_path),
                "detection_image": StorageService.absolute_to_public(detection_path),
            },
            "summary": "Phát hiện vùng nghi ngờ gãy xương tại đầu dưới xương quay",
        }
