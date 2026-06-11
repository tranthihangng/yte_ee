from pathlib import Path
from uuid import uuid4

import numpy as np

from app.core.config import settings
from app.services.storage_service import to_public_path
from app.utils.image_utils import ensure_rgb_copy

try:
    import cv2
    import tensorflow as tf
    from tensorflow.keras.applications.resnet50 import preprocess_input
    from tensorflow.keras.models import load_model as keras_load_model
    from tensorflow.keras.utils import img_to_array, load_img
except Exception:  # pragma: no cover - optional runtime dependency
    cv2 = None
    tf = None
    preprocess_input = None
    keras_load_model = None
    img_to_array = None
    load_img = None


_MODEL = None
_MODEL_LOAD_FAILED = False
_CLASS_NAMES = ["lung_aca", "lung_n", "lung_scc"]
_LABEL_MAP = {
    "lung_aca": "Lung adenocarcinoma",
    "lung_n": "Lung benign/normal",
    "lung_scc": "Lung squamous cell carcinoma",
}
_IMG_SIZE = (224, 224)


def _resolve_weight_path() -> Path:
    project_root = Path(__file__).resolve().parents[6]
    return project_root / "gd" / "his" / "best_resnet50_lung.keras"


def load_model():
    global _MODEL, _MODEL_LOAD_FAILED
    if _MODEL is not None:
        return _MODEL
    if _MODEL_LOAD_FAILED:
        raise RuntimeError("Histopath model load failed previously.")
    if keras_load_model is None:
        _MODEL_LOAD_FAILED = True
        raise RuntimeError("Missing dependency: tensorflow")
    model_path = _resolve_weight_path()
    if not model_path.exists():
        _MODEL_LOAD_FAILED = True
        raise RuntimeError(f"Histopath model not found: {model_path}")
    try:
        _MODEL = keras_load_model(str(model_path))
        return _MODEL
    except Exception as exc:
        _MODEL_LOAD_FAILED = True
        raise RuntimeError(f"Failed to load histopath model: {exc}") from exc


def _find_last_conv_layer_name(model) -> str:
    for layer in reversed(model.layers):
        output_shape = getattr(layer, "output_shape", None)
        if output_shape is not None and len(output_shape) == 4:
            return layer.name
    raise RuntimeError("No convolutional layer found for Grad-CAM")


def _gradcam_heatmap(model, img_batch: np.ndarray, pred_index: int) -> np.ndarray:
    if tf is None:
        raise RuntimeError("Tensorflow unavailable for Grad-CAM")
    last_conv_layer_name = "conv5_block3_out"
    try:
        model.get_layer(last_conv_layer_name)
    except Exception:
        last_conv_layer_name = _find_last_conv_layer_name(model)
    model_output = model.output[0] if isinstance(model.output, list) else model.output
    grad_model = tf.keras.models.Model(
        inputs=model.input,
        outputs=[model.get_layer(last_conv_layer_name).output, model_output],
    )
    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_batch, training=False)
        if isinstance(predictions, (list, tuple)):
            predictions = predictions[0]
        class_channel = predictions[:, pred_index]
    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(conv_outputs * pooled_grads, axis=-1)
    heatmap = tf.maximum(heatmap, 0) / (tf.reduce_max(heatmap) + 1e-8)
    return heatmap.numpy()


def _save_gradcam_overlay(original_path: str, heatmap: np.ndarray, out_path: str) -> str:
    if cv2 is None:
        raise RuntimeError("Missing dependency: opencv-python")
    orig = cv2.imread(original_path)
    if orig is None:
        raise RuntimeError(f"Cannot read image for Grad-CAM: {original_path}")
    heatmap_uint8 = np.uint8(255 * heatmap)
    heatmap_resized = cv2.resize(heatmap_uint8, (orig.shape[1], orig.shape[0]))
    heatmap_color = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
    blended = cv2.addWeighted(orig, 0.6, heatmap_color, 0.4, 0)
    cv2.imwrite(out_path, blended)
    return out_path


def predict(file_path: str, confidence_threshold: float = 0.5) -> dict:
    if load_img is None or img_to_array is None or preprocess_input is None:
        raise RuntimeError("Missing tensorflow preprocessing dependencies")
    model = load_model()
    original = ensure_rgb_copy(file_path, str(settings.gradcam_dir / f"histo_original_{uuid4().hex}.png"))
    img = load_img(file_path, target_size=_IMG_SIZE)
    img_array = img_to_array(img)
    img_batch = np.expand_dims(img_array, axis=0)
    img_batch = preprocess_input(img_batch)
    pred = model.predict(img_batch, verbose=0)
    pred_idx = int(np.argmax(pred[0]))
    pred_class = _CLASS_NAMES[pred_idx]
    pred_conf = float(pred[0][pred_idx])

    heatmap = _gradcam_heatmap(model, img_batch, pred_idx)
    gradcam_path = _save_gradcam_overlay(original, heatmap, str(settings.gradcam_dir / f"histo_gradcam_{uuid4().hex}.png"))
    top_indices = np.argsort(pred[0])[::-1][:3]
    top_classes = [_LABEL_MAP.get(_CLASS_NAMES[i], _CLASS_NAMES[i]) for i in top_indices]
    confidence = max(float(confidence_threshold), pred_conf)
    label_display = _LABEL_MAP.get(pred_class, pred_class)
    return {
        "module": "histopath",
        "predicted_label": label_display,
        "confidence": max(0.5, min(0.99, confidence)),
        "metrics": {
            "top1": top_classes[0],
            "top2": top_classes[1] if len(top_classes) > 1 else top_classes[0],
            "top3": top_classes[2] if len(top_classes) > 2 else top_classes[-1],
            "class_probabilities": {cls: float(prob) for cls, prob in zip(_CLASS_NAMES, pred[0].tolist())},
        },
        "artifacts": {"original_image": to_public_path(original), "gradcam_image": to_public_path(gradcam_path)},
        "summary": f"Mô hình phân loại: {label_display}",
    }
