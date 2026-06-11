from app.utils.preprocess_utils import save_rgb_resized

INPUT_SIZE = (640, 640)


def preprocess(file_path: str) -> str:
    """Tiền xử lý ảnh đếm lao: RGB, resize 640."""
    return save_rgb_resized(file_path, "tuberculosis_counting", INPUT_SIZE)
