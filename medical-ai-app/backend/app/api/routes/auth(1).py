from fastapi import APIRouter

from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def get_me():
    return get_current_user()
