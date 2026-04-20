from pathlib import Path

from PIL import Image


def blend_overlay(base_path: str, mask_path: str, out_path: str, alpha: float = 0.35) -> str:
    base = Image.open(base_path).convert("RGBA")
    mask = Image.open(mask_path).convert("RGBA").resize(base.size)
    output = Image.blend(base, mask, alpha=alpha)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    output.save(out)
    return str(out)
