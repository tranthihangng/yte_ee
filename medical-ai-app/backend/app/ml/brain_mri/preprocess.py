from pathlib import Path

from app.utils.preprocess_utils import save_rgb_resized

INPUT_SIZE = (224, 224)
VOLUME_EXTENSIONS = (".npy", ".nii", ".nii.gz", ".dcm")


def preprocess(file_path: str) -> str:
    """Tiền xử lý ảnh MRI: volume giữ nguyên, ảnh 2D resize 224."""
    lower_name = Path(file_path).name.lower()
    if lower_name.endswith(VOLUME_EXTENSIONS):
        return file_path
    return save_rgb_resized(file_path, "brain_mri", INPUT_SIZE)
