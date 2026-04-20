from pathlib import Path

from PIL import Image, ImageOps


def ensure_rgb_copy(source: str, target: str) -> str:
    src = Path(source)
    dst = Path(target)
    dst.parent.mkdir(parents=True, exist_ok=True)
    image = Image.open(src).convert("RGB")
    image.save(dst)
    return str(dst)


def make_thumbnail(source: str, target: str, size: tuple[int, int] = (512, 512)) -> str:
    image = Image.open(source).convert("RGB")
    image = ImageOps.contain(image, size)
    Path(target).parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    return target
