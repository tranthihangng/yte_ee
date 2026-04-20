from fastapi import APIRouter

router = APIRouter(prefix="/settings")


@router.get("")
def get_settings():
    return {
        "theme": "light",
        "default_threshold": 0.8,
        "output_dir": "outputs",
        "system_name": "MedAI Assist",
        "model_version": "v1.2.0",
        "report_template": "standard",
        "database_engine": "sqlite",
    }
