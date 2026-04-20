from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, cases, dashboard, health, prediction, reports, settings as settings_route
from app.core.config import settings
from app.core.database import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    settings.overlays_dir.mkdir(parents=True, exist_ok=True)
    settings.masks_dir.mkdir(parents=True, exist_ok=True)
    settings.gradcam_dir.mkdir(parents=True, exist_ok=True)
    settings.detections_dir.mkdir(parents=True, exist_ok=True)

    app.include_router(health.router, prefix=settings.api_prefix, tags=["health"])
    app.include_router(auth.router, prefix=settings.api_prefix, tags=["auth"])
    app.include_router(dashboard.router, prefix=settings.api_prefix, tags=["dashboard"])
    app.include_router(cases.router, prefix=settings.api_prefix, tags=["cases"])
    app.include_router(prediction.router, prefix=settings.api_prefix, tags=["prediction"])
    app.include_router(reports.router, prefix=settings.api_prefix, tags=["reports"])
    app.include_router(settings_route.router, prefix=settings.api_prefix, tags=["settings"])
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")
    return app


app = create_app()
