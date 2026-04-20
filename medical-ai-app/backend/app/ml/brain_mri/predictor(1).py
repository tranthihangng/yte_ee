from __future__ import annotations

from pathlib import Path

from app.core.config import settings
from app.services.storage_service import StorageService
from app.ml.brain_mri.preprocess import preprocess
from app.ml.brain_mri.postprocess import postprocess
from app.utils.image_utils import save_rgb_image


class BrainMRIPredictor:
    def __init__(self) -> None:
        self.model = self.load_model()

    def load_model(self):
        """
        Thay phần này bằng logic load model thật của bạn.
        Ví dụ:
            model = torch.load("path/to/model.pt", map_location="cpu")
            model.eval()
            return model
        """
        return {"name": "brain-mri-stub"}

    def predict(self, file_path: str, confidence_threshold: float = 0.5) -> dict:
        image = preprocess(file_path)
        overlay, mask = postprocess(image)

        stem = Path(file_path).stem
        original_path = settings.overlays_dir / f"{stem}_brain_original.png"
        overlay_path = settings.overlays_dir / f"{stem}_brain_overlay.png"
        mask_path = settings.masks_dir / f"{stem}_brain_mask.png"

        save_rgb_image(image, original_path)
        save_rgb_image(overlay, overlay_path)
        save_rgb_image(mask, mask_path)

        return {
            "module": "brain_mri",
            "predicted_label": "U não vùng trán",
            "confidence": max(0.74, confidence_threshold + 0.14),
            "metrics": {
                "dice": 0.891,
                "area_cm2": 18.37,
            },
            "artifacts": {
                "original_image": StorageService.absolute_to_public(original_path),
                "overlay_image": StorageService.absolute_to_public(overlay_path),
                "mask_image": StorageService.absolute_to_public(mask_path),
            },
            "summary": "Vùng tăng tín hiệu bất thường tại thùy trán phải",
        }
