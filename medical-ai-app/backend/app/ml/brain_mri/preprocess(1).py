from PIL import Image

from app.utils.image_utils import open_medical_image


def preprocess(file_path: str) -> Image.Image:
    return open_medical_image(file_path).convert("RGB")
