from app.utils.preprocess_utils import save_rgb_resized

INPUT_SIZE = (224, 224)


def preprocess(file_path: str) -> str:
    """Tiền xử lý ảnh mô bệnh học: RGB, resize 224."""
    return save_rgb_resized(file_path, "histopath", INPUT_SIZE)
