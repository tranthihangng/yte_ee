from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120), default="Nguyễn Thị An")
    role: Mapped[str] = mapped_column(String(80), default="Bác sĩ / Quản trị viên")
    email: Mapped[str] = mapped_column(String(150), unique=True, default="admin@medai.local")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
