from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MedAI Assist API"
    app_version: str = "1.0.0"
    api_prefix: str = "/api"
    debug: bool = True

    backend_dir: Path = Path(__file__).resolve().parents[3]
    uploads_dir: Path = backend_dir / "uploads"
    outputs_dir: Path = backend_dir / "outputs"
    reports_dir: Path = outputs_dir / "reports"
    overlays_dir: Path = outputs_dir / "overlays"
    masks_dir: Path = outputs_dir / "masks"
    gradcam_dir: Path = outputs_dir / "gradcam"
    detections_dir: Path = outputs_dir / "detections"

    database_url: str = f"sqlite:///{(backend_dir / 'medical_ai.db').as_posix()}"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    default_system_name: str = "MedAI Assist"
    default_output_directory: str = "outputs"
    default_confidence_threshold: float = 0.8
    report_logo_enabled: bool = True
    report_signature_name: str = "TS.BS. Trần Minh Đức"
    report_signature_title: str = "Chuyên khoa Chẩn đoán hình ảnh"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def ensure_directories(self) -> None:
        for folder in [
            self.uploads_dir,
            self.outputs_dir,
            self.reports_dir,
            self.overlays_dir,
            self.masks_dir,
            self.gradcam_dir,
            self.detections_dir,
        ]:
            folder.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
