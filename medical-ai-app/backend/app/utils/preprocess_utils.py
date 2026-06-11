from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps

from app.core.config import settings


def save_rgb_resized(file_path: str, module_type: str, size: tuple[int, int]) -> str:
    src = Path(file_path)
    out_dir = settings.upload_dir / "preprocessed" / module_type
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{uuid4().hex}{src.suffix or '.png'}"

    image = Image.open(src).convert("RGB")
    image = ImageOps.contain(image, size)
    canvas = Image.new("RGB", size, (0, 0, 0))
    offset = ((size[0] - image.width) // 2, (size[1] - image.height) // 2)
    canvas.paste(image, offset)
    canvas.save(target)
    return str(target)
