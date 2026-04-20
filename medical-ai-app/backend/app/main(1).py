from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import auth, cases, dashboard, health, prediction, reports, settings as settings_route
from app.core.config import settings
from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(dashboard.router, prefix=settings.api_prefix)
app.include_router(cases.router, prefix=settings.api_prefix)
app.include_router(prediction.router, prefix=settings.api_prefix)
app.include_router(reports.router, prefix=settings.api_prefix)
app.include_router(settings_route.router, prefix=settings.api_prefix)

app.mount("/uploads", StaticFiles(directory=settings.uploads_dir), name="uploads")
app.mount("/outputs", StaticFiles(directory=settings.outputs_dir), name="outputs")


@app.get("/")
def root():
    return {"message": "MedAI Assist API", "docs": "/docs"}
