from pathlib import Path
from uuid import uuid4
from collections import Counter

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
_CANONICAL_LABELS = {
    "bone anomaly": "bone anomaly",
    "bone_anomaly": "bone anomaly",
    "boneanomaly": "bone anomaly",
    "bone lesion": "bone lesion",
    "bone_lesion": "bone lesion",
    "bonelesion": "bone lesion",
    "foreign body": "foreign body",
    "foreign_body": "foreign body",
    "foreignbody": "foreign body",
    "fracture": "fracture",
    "metal": "metal",
    "periosteal reaction": "periosteal reaction",
    "periosteal_reaction": "periosteal reaction",
    "periostealreaction": "periosteal reaction",
    "pronator sign": "pronator sign",
    "pronator_sign": "pronator sign",
    "pronatorsign": "pronator sign",
    "soft tissue": "soft tissue",
    "soft_tissue": "soft tissue",
    "softtissue": "soft tissue",
    "text": "text",
}
_VI_LABEL = {
    "bone anomaly": "Bất thường xương",
    "bone lesion": "Tổn thương xương",
    "foreign body": "Dị vật",
    "fracture": "Gãy xương",
    "metal": "Vật liệu kim loại",
    "periosteal reaction": "Phản ứng màng xương",
    "pronator sign": "Dấu hiệu pronator quadratus",
    "soft tissue": "Tổn thương mô mềm",
    "text": "Ký tự/nhãn chữ trên phim",
    "normal": "Không ghi nhận bất thường rõ",
}
_NON_CLINICAL_LABELS = {"text", "metal"}
_CLINICAL_PRIORITY = [
    "fracture",
    "periosteal reaction",
    "bone lesion",
    "bone anomaly",
    "pronator sign",
    "soft tissue",
    "foreign body",
]


def _normalize_label(raw: str) -> str:
    key = raw.strip().lower().replace("-", " ").replace("__", "_")
    return _CANONICAL_LABELS.get(key, raw.strip().lower())


def _pick_primary_clinical_label(class_counts: Counter[str]) -> str:
    for candidate in _CLINICAL_PRIORITY:
        if class_counts.get(candidate, 0) > 0:
            return candidate
    return "normal"


def _max_confidence_for_label(labels: list[tuple[str, float]], target: str) -> float:
    confs = [conf for label, conf in labels if label == target]
    return max(confs) if confs else 0.0


def _mean_confidence_for_labels(labels: list[tuple[str, float]], accepted_labels: set[str]) -> float:
    confs = [conf for label, conf in labels if label in accepted_labels]
    return float(sum(confs) / len(confs)) if confs else 0.0


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


def _predict_with_yolo(file_path: str, confidence_threshold: float, out_path: str) -> tuple[float, int, list[tuple[str, float]]]:
    model = load_model()
    if model is None or cv2 is None:
        return 0.0, 0, []
    results = model.predict(source=file_path, conf=confidence_threshold, save=False, verbose=False)
    plotted = results[0].plot()  # BGR image
    cv2.imwrite(out_path, plotted)
    detections = len(results[0].boxes) if results and results[0].boxes is not None else 0
    confs = results[0].boxes.conf.cpu().tolist() if detections > 0 else []
    classes = results[0].boxes.cls.cpu().tolist() if detections > 0 else []
    names = results[0].names if results else {}
    labels: list[tuple[str, float]] = []
    for cls_idx, conf in zip(classes, confs):
        raw_name = str(names.get(int(cls_idx), str(int(cls_idx))))
        labels.append((_normalize_label(raw_name), float(conf)))
    confidence = max(confs) if confs else 0.0
    return float(confidence), int(detections), labels


def predict(file_path: str, confidence_threshold: float = 0.5) -> dict:
    original = ensure_rgb_copy(file_path, str(settings.detections_dir / f"xray_original_{uuid4().hex}.png"))
    detection = str(settings.detections_dir / f"xray_detection_{uuid4().hex}.png")
    _global_confidence, detections, labels = _predict_with_yolo(file_path, confidence_threshold, detection)
    if detections == 0:
        detection = ensure_rgb_copy(file_path, detection)
    class_counts = Counter(label for label, _ in labels)
    clinical_counts = Counter({name: count for name, count in class_counts.items() if name not in _NON_CLINICAL_LABELS})

    if detections > 0 and clinical_counts:
        predicted_label = _pick_primary_clinical_label(clinical_counts)
        confidence = _mean_confidence_for_labels(labels, set(clinical_counts.keys()))
        top_vi = _VI_LABEL.get(predicted_label, predicted_label)
        mix = ", ".join(f"{_VI_LABEL.get(name, name)} ({count})" for name, count in clinical_counts.most_common(4))
        summary = (
            f"Kết luận ưu tiên lâm sàng vùng cổ tay: {top_vi}. "
            f"Các dấu hiệu liên quan: {mix}. "
            "Khuyến nghị đối chiếu lâm sàng và đọc phim bởi bác sĩ chẩn đoán hình ảnh."
        )
    else:
        predicted_label = "normal"
        confidence = 0.0
        if detections > 0 and class_counts:
            aux = ", ".join(f"{_VI_LABEL.get(name, name)} ({count})" for name, count in class_counts.most_common(3))
            summary = (
                "Không ghi nhận dấu hiệu tổn thương cổ tay có ý nghĩa lâm sàng theo ngưỡng hiện tại. "
                f"Các phát hiện phụ (không dùng làm chẩn đoán chính): {aux}."
            )
        else:
            summary = "Không ghi nhận bất thường rõ vùng cổ tay theo ngưỡng hiện tại."
    return {
        "module": "wrist_xray",
        "predicted_label": predicted_label,
        "confidence": max(0.0, min(0.99, confidence)),
        "metrics": {
            "detections": detections,
            "class_counts": dict(class_counts),
            "clinical_class_counts": dict(clinical_counts),
            "label_vi": _VI_LABEL.get(predicted_label, predicted_label),
        },
        "artifacts": {"original_image": to_public_path(original), "detection_image": to_public_path(detection)},
        "summary": summary,
    }
