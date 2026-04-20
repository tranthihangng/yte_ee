from typing import TypedDict


class CurrentUser(TypedDict):
    name: str
    role: str
    initials: str


def get_current_user() -> CurrentUser:
    return {
        "name": "Nguyễn Thị An",
        "role": "Bác sĩ / Quản trị viên",
        "initials": "NT",
    }
