from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.utils.export_utils import public_path
from app.utils.image_utils import make_preview_image


class StorageService:
    @staticmethod
    def save_upload(file: UploadFile, module_type: str) -> tuple[str, str]:
        suffix = Path(file.filename or "").suffix.lower()
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        stem = Path(file.filename or "upload").stem.replace(" ", "_")
        unique_name = f"{module_type}_{stem}_{timestamp}_{uuid4().hex[:8]}{suffix}"
        absolute_path = settings.uploads_dir / unique_name

        with absolute_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        preview_name = f"{absolute_path.stem}_preview.png"
        preview_path = settings.uploads_dir / preview_name
        make_preview_image(absolute_path, preview_path)

        return str(absolute_path), public_path(preview_path, settings.backend_dir)

    @staticmethod
    def absolute_to_public(path: str | Path) -> str:
        return public_path(path, settings.backend_dir)
