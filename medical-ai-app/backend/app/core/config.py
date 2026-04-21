from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "MedAI Assist API"
    api_prefix: str = "/api"
    debug: bool = True
    secret_key: str = "change-me-in-production"
    database_url: str = f"sqlite:///{BASE_DIR / 'medical_ai.db'}"
    upload_dir: Path = BASE_DIR / "uploads"
    output_dir: Path = BASE_DIR / "outputs"
    reports_dir: Path = BASE_DIR / "outputs" / "reports"
    overlays_dir: Path = BASE_DIR / "outputs" / "overlays"
    masks_dir: Path = BASE_DIR / "outputs" / "masks"
    gradcam_dir: Path = BASE_DIR / "outputs" / "gradcam"
    detections_dir: Path = BASE_DIR / "outputs" / "detections"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_use_tls: bool = True
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
