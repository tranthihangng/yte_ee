from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter(prefix="/auth")


USERS_FILE = Path(settings.users_file)
TOKEN_EXPIRE_HOURS = 8


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=5)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def _b64url_decode(raw: str) -> bytes:
    pad = "=" * ((4 - len(raw) % 4) % 4)
    return base64.urlsafe_b64decode(raw + pad)


def _make_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)).timestamp()),
    }
    payload_raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    payload_part = _b64url_encode(payload_raw)
    sig = hmac.new(settings.secret_key.encode("utf-8"), payload_part.encode("utf-8"), hashlib.sha256).digest()
    return f"{payload_part}.{_b64url_encode(sig)}"


def _read_users() -> list[dict[str, Any]]:
    if not USERS_FILE.exists():
        raise HTTPException(status_code=500, detail=f"Users file not found: {USERS_FILE}")
    try:
        parsed = json.loads(USERS_FILE.read_text(encoding="utf-8"))
        if not isinstance(parsed, list):
            raise ValueError("users JSON must be a list")
        return parsed
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail=f"Invalid users file format: {exc}") from exc


def _write_users(users: list[dict[str, Any]]) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt_bytes = salt or hashlib.sha256(str(datetime.now(timezone.utc).timestamp()).encode("utf-8")).digest()[:16]
    iterations = 120_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, iterations)
    return f"pbkdf2_sha256${iterations}${salt_bytes.hex()}${digest.hex()}"


def _verify_password(password: str, hashed: str) -> bool:
    try:
        algo, iterations, salt_hex, digest_hex = hashed.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False
        check = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        ).hex()
        return hmac.compare_digest(check, digest_hex)
    except ValueError:
        return False


def _check_user_password(password: str, user: dict[str, Any]) -> bool:
    hashed = str(user.get("password_hash", "")).strip()
    if hashed:
        return _verify_password(password, hashed)
    # Backward-compatible plain-text mode for simple JSON edits in local deployments.
    plain = str(user.get("password", ""))
    return bool(plain) and hmac.compare_digest(plain, password)


def _get_bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    return authorization.split(" ", 1)[1].strip()


def _decode_token(token: str) -> dict[str, Any]:
    try:
        payload_part, sig_part = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    expected_sig = hmac.new(settings.secret_key.encode("utf-8"), payload_part.encode("utf-8"), hashlib.sha256).digest()
    provided_sig = _b64url_decode(sig_part)
    if not hmac.compare_digest(expected_sig, provided_sig):
        raise HTTPException(status_code=401, detail="Invalid token signature")
    payload = json.loads(_b64url_decode(payload_part).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=401, detail="Token expired")
    return payload


def _sanitize_user(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "username": user.get("username", ""),
        "full_name": user.get("full_name", user.get("username", "")),
        "role": user.get("role", "user"),
        "active": bool(user.get("active", True)),
        "must_change_password": bool(user.get("must_change_password", False)),
    }


@router.post("/login")
def login(payload: LoginRequest):
    users = _read_users()
    username = payload.username.strip()
    user = next((entry for entry in users if entry.get("username") == username), None)
    if not user or not _check_user_password(payload.password, user):
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
    if not user.get("active", True):
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    return {
        "access_token": _make_token(username),
        "token_type": "bearer",
        "user": _sanitize_user(user),
    }


@router.get("/me")
def me(authorization: str | None = Header(default=None)):
    token = _get_bearer_token(authorization)
    payload = _decode_token(token)
    username = str(payload.get("sub", ""))
    users = _read_users()
    user = next((entry for entry in users if entry.get("username") == username), None)
    if not user:
        raise HTTPException(status_code=401, detail="Tài khoản không tồn tại")
    if not user.get("active", True):
        raise HTTPException(status_code=403, detail="Tài khoản đã bị khóa")
    return _sanitize_user(user)


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    authorization: str | None = Header(default=None),
):
    token = _get_bearer_token(authorization)
    username = str(_decode_token(token).get("sub", ""))
    users = _read_users()
    target = next((entry for entry in users if entry.get("username") == username), None)
    if not target:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    if not _check_user_password(payload.old_password, target):
        raise HTTPException(status_code=400, detail="Mật khẩu cũ không đúng")
    target["password_hash"] = _hash_password(payload.new_password)
    target.pop("password", None)
    target["must_change_password"] = False
    _write_users(users)
    return {"message": "Đổi mật khẩu thành công"}
