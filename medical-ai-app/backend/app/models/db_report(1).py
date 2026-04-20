from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), nullable=False, index=True)
    template_type: Mapped[str] = mapped_column(String(50), default="standard")
    include_images: Mapped[bool] = mapped_column(Boolean, default=True)
    include_metrics: Mapped[bool] = mapped_column(Boolean, default=True)
    include_notes: Mapped[bool] = mapped_column(Boolean, default=True)
    mask_personal_info: Mapped[bool] = mapped_column(Boolean, default=False)
    pdf_path: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="reports")
