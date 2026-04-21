from pathlib import Path
from uuid import uuid4

from app.core.config import settings
from app.services.storage_service import to_public_path
from app.utils.image_utils import ensure_rgb_copy

try:
    import cv2
    from ultralytics import YOLO
except Exception:  # pragma: no cover - optional runtime dependency
    cv2 = None
    YOLO = None


_MODEL = None


def _resolve_weight_path() -> Path:
    project_root = Path(__file__).resolve().parents[6]
    return project_root / "gd" / "tuberculosis_counting" / "best.pt"


def load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if YOLO is None:
        raise RuntimeError("Missing dependency: ultralytics")
    weight_path = _resolve_weight_path()
    if not weight_path.exists():
        raise RuntimeError(f"Tuberculosis model not found: {weight_path}")
    _MODEL = YOLO(str(weight_path))
    return _MODEL


def predict(file_path: str, confidence_threshold: float = 0.25) -> dict:
    if cv2 is None:
        raise RuntimeError("Missing dependency: opencv-python")
    model = load_model()
    original = ensure_rgb_copy(file_path, str(settings.detections_dir / f"tb_original_{uuid4().hex}.png"))
    detection = str(settings.detections_dir / f"tb_detection_{uuid4().hex}.png")
    results = model.predict(source=file_path, conf=confidence_threshold, save=False, verbose=False)
    result = results[0]
    plotted = result.plot()
    cv2.imwrite(detection, plotted)
    detections = len(result.boxes) if result.boxes is not None else 0
    confs = result.boxes.conf.cpu().tolist() if detections > 0 else []
    confidence = float(max(confs)) if confs else max(0.5, confidence_threshold)
    label = f"Detected {detections} bacilli" if detections > 0 else "No bacilli detected"
    return {
        "module": "tuberculosis_counting",
        "predicted_label": label,
        "confidence": max(0.5, min(0.99, confidence)),
        "metrics": {"detections": int(detections), "count": int(detections)},
        "artifacts": {
            "original_image": to_public_path(original),
            "detection_image": to_public_path(detection),
        },
        "summary": (
            f"YOLO phát hiện {detections} vùng nghi vi khuẩn Mycobacterium tuberculosis"
            if detections > 0
            else "Không phát hiện vùng nghi vi khuẩn theo ngưỡng hiện tại"
        ),
    }
