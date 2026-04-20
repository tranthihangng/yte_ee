from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ModuleType(str, Enum):
    BRAIN_MRI = "brain_mri"
    HISTOPATH = "histopath"
    WRIST_XRAY = "wrist_xray"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    SAVED = "saved"
    PENDING_CONFIRMATION = "pending_confirmation"
    ERROR = "error"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    patient_name: Mapped[str] = mapped_column(String(255), default="")
    patient_identifier: Mapped[str] = mapped_column(String(100), default="")
    study_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    module_type: Mapped[ModuleType] = mapped_column(SAEnum(ModuleType), nullable=False)
    input_file_path: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[CaseStatus] = mapped_column(SAEnum(CaseStatus), default=CaseStatus.SAVED)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prediction_results = relationship("PredictionResult", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="case", cascade="all, delete-orphan")
