from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


def save_upload(file: UploadFile, module: str) -> str:
    ext = Path(file.filename or "image.png").suffix
    filename = f"{module}_{uuid4().hex}{ext}"
    target = settings.upload_dir / filename
    with target.open("wb") as out:
        out.write(file.file.read())
    return str(target)


def to_public_path(path: str) -> str:
    p = Path(path)
    if "uploads" in p.parts:
        return f"/uploads/{p.name}"
    if "outputs" in p.parts:
        folder = p.parent.name
        return f"/outputs/{folder}/{p.name}"
    return path
