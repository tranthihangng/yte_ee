from fastapi import APIRouter

router = APIRouter()


@router.get("/auth/me")
def me():
    return {"name": "Nguyễn Thị An", "role": "Bác sĩ / Quản trị viên", "initials": "NT"}
