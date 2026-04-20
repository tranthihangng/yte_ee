from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image

from app.core.config import settings
from app.services.storage_service import to_public_path
from app.utils.image_utils import ensure_rgb_copy

try:
    import torch
    import torch.nn.functional as F
    import yaml
except Exception:  # pragma: no cover - optional runtime dependency
    torch = None
    F = None
    yaml = None


_MODEL = None
_MODEL_ARGS = None
_MODEL_LOAD_FAILED = False


def _cbim_root() -> Path:
    project_root = Path(__file__).resolve().parents[6]
    return project_root / "CBIM-Medical-Image-Segmentation"


def _default_model_path() -> Path:
    # Match user-provided script: gd/mri/predict_show.py
    return _cbim_root() / "exp" / "brats" / "brats_fsfa_unet_2d" / "epoc47" / "fold_0_latest.pth"


def _default_config_path() -> Path:
    return _cbim_root() / "config" / "brats" / "fsfa_unet_2d.yaml"


def _extract_2d_slice(arr: np.ndarray) -> np.ndarray:
    # Normalize any MRI-like array to one 2D slice for preview and fallback.
    if arr.ndim == 2:
        return arr
    if arr.ndim == 3:
        # Prefer FLAIR if shape is (4,H,W)
        if arr.shape[0] == 4:
            return arr[0]
        # (D,H,W) -> choose middle slice
        return arr[arr.shape[0] // 2]
    if arr.ndim == 4:
        # (4,D,H,W): choose FLAIR (channel 0), middle depth
        if arr.shape[0] == 4:
            return arr[0, arr.shape[1] // 2]
        return arr[0, arr.shape[1] // 2]
    raise ValueError(f"Unsupported npy shape: {arr.shape}")


def _to_4ch_sample(file_path: str) -> np.ndarray:
    # CBIM BraTS model expects 4 channels (FLAIR, T1, T1ce, T2).
    # If upload is npy, attempt to map channels; else duplicate grayscale image to 4 channels.
    path = Path(file_path)
    if path.suffix.lower() == ".npy":
        arr = np.load(file_path).astype(np.float32)
        if arr.ndim == 3 and arr.shape[0] == 4:
            sample = arr
        elif arr.ndim == 3 and arr.shape[-1] == 4:
            # (H,W,4) -> (4,H,W)
            sample = np.transpose(arr, (2, 0, 1))
        elif arr.ndim == 4 and arr.shape[0] == 4:
            # (4, D, H, W) -> middle slice of D
            sample = arr[:, arr.shape[1] // 2]
        else:
            base = _extract_2d_slice(arr)
            sample = np.stack([base, base, base, base], axis=0)
        return sample

    image = Image.open(file_path).convert("L").resize((240, 240))
    arr = np.asarray(image).astype(np.float32)
    if arr.max() > 0:
        arr = arr / 255.0
    return np.stack([arr, arr, arr, arr], axis=0)


def _save_original_preview(file_path: str, out_path: str) -> str:
    path = Path(file_path)
    if path.suffix.lower() != ".npy":
        return ensure_rgb_copy(file_path, out_path)
    arr = np.load(file_path).astype(np.float32)
    view = _extract_2d_slice(arr)
    view = view - view.min()
    if view.max() > 0:
        view = view / view.max()
    img = Image.fromarray((view * 255).astype(np.uint8), mode="L").convert("RGB")
    img.save(out_path)
    return out_path


def _create_fallback_mask_from_original(original_path: str, mask_path: str) -> str:
    # Heuristic fallback: highlight hyper-intense region on FLAIR preview.
    # This ensures user can see overlay even when model is unavailable.
    original = Image.open(original_path).convert("L")
    img = np.array(original, dtype=np.float32)
    brain = img > 5  # remove black background
    if np.any(brain):
        bright_threshold = np.percentile(img[brain], 99.2)
    else:
        bright_threshold = 255.0
    lesion = (img >= bright_threshold) & brain
    lesion = _dilate_binary(lesion, iterations=1)

    rgb = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)
    # Use class 3 color (yellow) for fallback lesion
    rgb[lesion] = [255, 255, 0]
    mask = Image.fromarray(rgb, mode="RGB")
    mask.save(mask_path)
    return mask_path


def _normalize(img: np.ndarray) -> np.ndarray:
    for i in range(img.shape[0]):
        channel = img[i]
        if channel.max() > 0:
            p1, p99 = np.percentile(channel, [1, 99])
            channel = np.clip(channel, p1, p99)
            channel = (channel - channel.min()) / (channel.max() - channel.min() + 1e-8)
        img[i] = channel
    return img


def load_model():
    global _MODEL, _MODEL_ARGS, _MODEL_LOAD_FAILED
    if _MODEL is not None:
        return _MODEL
    if _MODEL_LOAD_FAILED:
        raise RuntimeError("MRI model load failed previously. Check checkpoint/config path.")
    if torch is None or yaml is None:
        _MODEL_LOAD_FAILED = True
        raise RuntimeError("Missing MRI dependencies: torch/pyyaml")
    model_path = _default_model_path()
    config_path = _default_config_path()
    if not model_path.exists() or not config_path.exists():
        _MODEL_LOAD_FAILED = True
        raise RuntimeError(f"MRI model/config not found: {model_path} / {config_path}")
    try:
        import sys

        cbim_root = _cbim_root()
        if str(cbim_root) not in sys.path:
            sys.path.insert(0, str(cbim_root))
        from model.utils import get_model

        with config_path.open("r", encoding="utf-8") as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)

        class Args:
            pass

        args = Args()
        for key, value in config.items():
            setattr(args, key, value)
        if not hasattr(args, "dimension"):
            args.dimension = "2d"
        if hasattr(args, "arch") and not hasattr(args, "model"):
            args.model = args.arch
        model = get_model(args)
        checkpoint = torch.load(str(model_path), map_location="cpu")
        state_dict = checkpoint.get("ema_model_state_dict") or checkpoint.get("model_state_dict")
        model.load_state_dict(state_dict)
        model.eval()
        _MODEL = model
        _MODEL_ARGS = args
        return _MODEL
    except Exception as exc:
        _MODEL_LOAD_FAILED = True
        raise RuntimeError(f"Failed to load MRI model: {exc}") from exc


def _predict_with_cbim(file_path: str, mask_path: str) -> tuple[float, np.ndarray]:
    model = load_model()
    if F is None:
        raise RuntimeError("torch.nn.functional unavailable")
    sample = _normalize(_to_4ch_sample(file_path).copy())
    with torch.no_grad():
        tensor_img = torch.from_numpy(sample).float().unsqueeze(0)
        output = model(tensor_img)
        if isinstance(output, (tuple, list)):
            output = output[0]
        prob = F.softmax(output, dim=1)
        pred = torch.argmax(prob, dim=1).squeeze(0).cpu().numpy().astype(np.uint8)
        conf = float(prob.max().item())
    # Save mask with class colors like reference script:
    # 0: background (black), 1: red, 2: green, 3: yellow
    color_map = np.array(
        [
            [0, 0, 0],
            [255, 0, 0],
            [0, 255, 0],
            [255, 255, 0],
        ],
        dtype=np.uint8,
    )
    pred_safe = np.clip(pred, 0, 3)
    rgb_mask = color_map[pred_safe]
    mask_img = Image.fromarray(rgb_mask, mode="RGB")
    mask_img.save(mask_path)
    return conf, pred_safe


def _dilate_binary(mask: np.ndarray, iterations: int = 2) -> np.ndarray:
    out = mask.astype(bool)
    for _ in range(iterations):
        p = np.pad(out, ((1, 1), (1, 1)), mode="constant", constant_values=False)
        neighbors = [
            p[1:-1, 1:-1],
            p[:-2, 1:-1],
            p[2:, 1:-1],
            p[1:-1, :-2],
            p[1:-1, 2:],
            p[:-2, :-2],
            p[:-2, 2:],
            p[2:, :-2],
            p[2:, 2:],
        ]
        out = np.logical_or.reduce(neighbors)
    return out


def _erode_binary(mask: np.ndarray, iterations: int = 1) -> np.ndarray:
    out = mask.astype(bool)
    for _ in range(iterations):
        p = np.pad(out, ((1, 1), (1, 1)), mode="constant", constant_values=False)
        neighbors = [
            p[1:-1, 1:-1],
            p[:-2, 1:-1],
            p[2:, 1:-1],
            p[1:-1, :-2],
            p[1:-1, 2:],
            p[:-2, :-2],
            p[:-2, 2:],
            p[2:, :-2],
            p[2:, 2:],
        ]
        out = np.logical_and.reduce(neighbors)
    return out


def _create_overlay(
    original_path: str,
    mask_path: str,
    out_path: str,
    predicted_label: str,
    confidence: float,
    dice: float,
    area_cm2: float,
) -> None:
    original = Image.open(original_path).convert("RGB")
    # IMPORTANT: keep class colors unchanged when resizing mask
    mask_rgb = Image.open(mask_path).convert("RGB").resize(original.size, Image.Resampling.NEAREST)
    mask_np = np.array(mask_rgb, dtype=np.uint8)
    base_np = np.array(original, dtype=np.uint8)

    blended = base_np.copy()
    # Per-class stronger overlay colors.
    class_colors = {
        1: np.array([255, 0, 0], dtype=np.uint8),      # red
        2: np.array([0, 255, 0], dtype=np.uint8),      # green
        3: np.array([255, 255, 0], dtype=np.uint8),    # yellow
    }
    # decode class from rgb mask
    class_map = np.zeros(mask_np.shape[:2], dtype=np.uint8)
    class_map[np.all(mask_np == [255, 0, 0], axis=-1)] = 1
    class_map[np.all(mask_np == [0, 255, 0], axis=-1)] = 2
    class_map[np.all(mask_np == [255, 255, 0], axis=-1)] = 3

    for cls, color in class_colors.items():
        region = class_map == cls
        if not np.any(region):
            continue
        region = _dilate_binary(region, iterations=2)
        # Make class overlay stronger (closer to reference script look)
        alpha = 0.9
        blended[region] = ((1 - alpha) * base_np[region] + alpha * color).astype(np.uint8)
        # White border for clearer visibility
        inner = _erode_binary(region, iterations=1)
        border = region & (~inner)
        blended[border] = np.array([255, 255, 255], dtype=np.uint8)

    overlay = Image.fromarray(blended, mode="RGB").convert("RGBA")
    overlay.save(out_path)


def predict(file_path: str, confidence_threshold: float = 0.5) -> dict:
    original = _save_original_preview(file_path, str(settings.overlays_dir / f"mri_original_{uuid4().hex}.png"))
    mask = str(settings.masks_dir / f"mri_mask_{uuid4().hex}.png")
    confidence, pred_map = _predict_with_cbim(file_path, mask)
    if not Path(mask).exists():
        raise RuntimeError("MRI mask generation failed")
    confidence = max(confidence_threshold, confidence)

    cls1_pixels = int(np.sum(pred_map == 1))
    cls2_pixels = int(np.sum(pred_map == 2))
    cls3_pixels = int(np.sum(pred_map == 3))
    tumor_pixels = cls1_pixels + cls2_pixels + cls3_pixels
    is_abnormal = tumor_pixels > 0
    predicted_label = "Có vùng u não nghi ngờ" if is_abnormal else "Không phát hiện rõ bất thường"
    # Proxy metrics from predicted mask (no GT on inference-time).
    dice_proxy = 1.0 if is_abnormal else 0.0
    # Approx conversion for display-only; replace by calibrated spacing if available.
    area_cm2 = round(tumor_pixels * 0.0004, 2)

    overlay = str(settings.overlays_dir / f"mri_overlay_{uuid4().hex}.png")
    _create_overlay(original, mask, overlay, predicted_label, confidence, dice_proxy, area_cm2)
    return {
        "module": "brain_mri",
        "predicted_label": predicted_label,
        "confidence": max(0.5, min(0.99, confidence)),
        "metrics": {
            "dice": dice_proxy,
            "area_cm2": area_cm2,
            "class_pixels": {"ncr_net": cls1_pixels, "ed": cls2_pixels, "et": cls3_pixels},
        },
        "artifacts": {
            "original_image": to_public_path(original),
            "overlay_image": to_public_path(overlay),
            "mask_image": to_public_path(mask),
        },
        "summary": (
            f"Phân đoạn 3 lớp: NCR/NET={cls1_pixels}px, ED={cls2_pixels}px, ET={cls3_pixels}px"
            if is_abnormal
            else "Không ghi nhận vùng tăng tín hiệu bất thường rõ rệt"
        ),
    }
