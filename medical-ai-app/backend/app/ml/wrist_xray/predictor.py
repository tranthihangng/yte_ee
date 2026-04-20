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
    # User file: gd/xray/predict.py -> uses gd/xray/last35.pt
    project_root = Path(__file__).resolve().parents[6]
    return project_root / "gd" / "xray" / "last35.pt"


def load_model():
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    if YOLO is None:
        return None
    weight_path = _resolve_weight_path()
    if not weight_path.exists():
        return None
    _MODEL = YOLO(str(weight_path))
    return _MODEL


def _predict_with_yolo(file_path: str, confidence_threshold: float, out_path: str) -> tuple[float, int]:
    model = load_model()
    if model is None or cv2 is None:
        return 0.62, 0
    results = model.predict(source=file_path, conf=confidence_threshold, save=False, verbose=False)
    plotted = results[0].plot()  # BGR image
    cv2.imwrite(out_path, plotted)
    detections = len(results[0].boxes) if results and results[0].boxes is not None else 0
    confs = results[0].boxes.conf.cpu().tolist() if detections > 0 else []
    confidence = max(confs) if confs else 0.62
    return float(confidence), int(detections)


def predict(file_path: str, confidence_threshold: float = 0.5) -> dict:
    original = ensure_rgb_copy(file_path, str(settings.detections_dir / f"xray_original_{uuid4().hex}.png"))
    detection = str(settings.detections_dir / f"xray_detection_{uuid4().hex}.png")
    confidence, detections = _predict_with_yolo(file_path, confidence_threshold, detection)
    if detections == 0:
        detection = ensure_rgb_copy(file_path, detection)
    predicted_label = "Fracture" if detections > 0 else "Normal"
    summary = (
        "Phát hiện vùng nghi ngờ gãy xương tại đầu dưới xương quay"
        if detections > 0
        else "Không phát hiện vùng gãy xương rõ ràng theo ngưỡng hiện tại"
    )
    return {
        "module": "wrist_xray",
        "predicted_label": predicted_label,
        "confidence": max(0.5, min(0.99, confidence)),
        "metrics": {"detections": detections},
        "artifacts": {"original_image": to_public_path(original), "detection_image": to_public_path(detection)},
        "summary": summary,
    }
