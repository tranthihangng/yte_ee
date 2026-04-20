from __future__ import annotations

import io
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

try:
    import nibabel as nib
except Exception:  # pragma: no cover
    nib = None

try:
    import pydicom
except Exception:  # pragma: no cover
    pydicom = None


SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
SUPPORTED_DICOM_SUFFIXES = {".dcm"}
SUPPORTED_NIFTI_SUFFIXES = {".nii", ".gz"}


def normalize_array_to_uint8(array: np.ndarray) -> np.ndarray:
    array = array.astype(np.float32)
    if array.size == 0:
        return np.zeros((256, 256), dtype=np.uint8)
    array = array - np.min(array)
    max_val = np.max(array)
    if max_val > 0:
        array = array / max_val
    return (array * 255).clip(0, 255).astype(np.uint8)


def open_medical_image(file_path: str | Path) -> Image.Image:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in SUPPORTED_IMAGE_SUFFIXES:
        return Image.open(path).convert("RGB")

    if suffix in SUPPORTED_DICOM_SUFFIXES and pydicom is not None:
        ds = pydicom.dcmread(str(path))
        pixels = normalize_array_to_uint8(ds.pixel_array)
        return Image.fromarray(pixels).convert("RGB")

    if suffix == ".gz" and path.name.endswith(".nii.gz") and nib is not None:
        nii = nib.load(str(path))
        volume = nii.get_fdata()
        slice_idx = volume.shape[-1] // 2
        pixels = normalize_array_to_uint8(volume[..., slice_idx])
        return Image.fromarray(pixels).convert("RGB")

    if suffix == ".nii" and nib is not None:
        nii = nib.load(str(path))
        volume = nii.get_fdata()
        slice_idx = volume.shape[-1] // 2
        pixels = normalize_array_to_uint8(volume[..., slice_idx])
        return Image.fromarray(pixels).convert("RGB")

    raise ValueError(f"Định dạng file chưa được hỗ trợ: {path.name}")


def save_rgb_image(image: Image.Image, output_path: str | Path, max_size: tuple[int, int] = (1200, 1200)) -> str:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img = image.convert("RGB")
    img.thumbnail(max_size)
    img.save(path, format="PNG")
    return str(path)


def make_preview_image(file_path: str | Path, output_path: str | Path) -> str:
    image = open_medical_image(file_path)
    return save_rgb_image(image, output_path)


def create_softened_copy(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    image = ImageOps.autocontrast(image)
    image = ImageEnhance.Contrast(image).enhance(1.05)
    return image.filter(ImageFilter.SMOOTH_MORE)
