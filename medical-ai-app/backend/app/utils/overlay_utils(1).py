from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFilter

from app.utils.image_utils import create_softened_copy


def make_brain_overlay(image: Image.Image) -> tuple[Image.Image, Image.Image]:
    base = create_softened_copy(image)
    width, height = base.size
    overlay = base.copy().convert("RGBA")
    mask = Image.new("L", base.size, 0)

    cx, cy = int(width * 0.64), int(height * 0.47)
    rx, ry = int(width * 0.12), int(height * 0.16)

    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=220)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=max(4, width // 80)))

    tinted = Image.new("RGBA", base.size, (52, 134, 255, 0))
    tinted.putalpha(mask)
    overlay.alpha_composite(tinted)
    outline = ImageDraw.Draw(overlay)
    outline.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(38, 110, 255, 255), width=max(2, width // 180))
    return overlay.convert("RGB"), mask.convert("RGB")


def make_gradcam(image: Image.Image) -> Image.Image:
    base = create_softened_copy(image).convert("RGB")
    width, height = base.size
    gradcam = base.copy().convert("RGBA")
    heat = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(heat)

    for i in range(8):
        alpha = max(18, 90 - i * 10)
        x0 = int(width * 0.15) + i * 6
        y0 = int(height * 0.12) + i * 6
        x1 = int(width * 0.82) - i * 8
        y1 = int(height * 0.78) - i * 8
        color = (255, 80 + i * 12, 30 + i * 18, alpha)
        draw.ellipse((x0, y0, x1, y1), fill=color)
    heat = heat.filter(ImageFilter.GaussianBlur(radius=max(8, width // 30)))
    gradcam.alpha_composite(heat)
    return gradcam.convert("RGB")


def make_detection_view(image: Image.Image) -> Image.Image:
    base = create_softened_copy(image).convert("RGB")
    width, height = base.size
    output = base.copy()
    draw = ImageDraw.Draw(output)
    box1 = (int(width * 0.42), int(height * 0.22), int(width * 0.72), int(height * 0.58))
    box2 = (int(width * 0.28), int(height * 0.58), int(width * 0.55), int(height * 0.82))
    draw.rounded_rectangle(box1, radius=12, outline="#1D71F2", width=max(3, width // 150))
    draw.rounded_rectangle(box2, radius=12, outline="#F59E0B", width=max(3, width // 150))
    draw.text((box1[0] + 10, box1[1] - 28), "fracture 0.92", fill="#1D71F2")
    draw.text((box2[0] + 10, box2[1] - 28), "metal 0.81", fill="#F59E0B")
    return output
