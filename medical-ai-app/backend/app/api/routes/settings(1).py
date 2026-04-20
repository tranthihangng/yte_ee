from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(prefix="/settings", tags=["settings"])

SETTINGS_FILE = settings.backend_dir / "app_settings.json"
DEFAULT_SETTINGS = {
    "system_name": settings.default_system_name,
    "theme": "light",
    "default_confidence_threshold": settings.default_confidence_threshold,
    "output_directory": str(settings.outputs_dir),
    "brain_mri_model_version": "BrainSeg v1.2.0",
    "histopath_model_version": "HistoClass v2.1.0",
    "wrist_xray_model_version": "WristDetect v1.0.0",
    "report_template": "standard",
    "database_url": settings.database_url,
}


def read_settings() -> dict:
    if not SETTINGS_FILE.exists():
        SETTINGS_FILE.write_text(json.dumps(DEFAULT_SETTINGS, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))


@router.get("")
def get_settings():
    return read_settings()


@router.put("")
def update_settings(payload: dict):
    current = read_settings()
    current.update(payload)
    SETTINGS_FILE.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    return current
