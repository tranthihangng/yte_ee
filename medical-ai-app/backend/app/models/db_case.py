from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Case(Base):
    __tablename__ = "cases"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    patient_name: Mapped[str] = mapped_column(String(120))
    patient_identifier: Mapped[str] = mapped_column(String(80))
    study_date: Mapped[date] = mapped_column(Date)
    module_type: Mapped[str] = mapped_column(String(50))
    input_file_path: Mapped[str] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="Đã lưu")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    predictions: Mapped[list["PredictionResult"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class PredictionResult(Base):
    __tablename__ = "prediction_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id"), index=True)
    predicted_label: Mapped[str] = mapped_column(String(120))
    confidence: Mapped[float] = mapped_column(Float)
    summary: Mapped[str] = mapped_column(Text)
    metrics_json: Mapped[str] = mapped_column(Text)
    artifacts_json: Mapped[str] = mapped_column(Text)
    raw_output_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    case: Mapped["Case"] = relationship(back_populates="predictions")


class SystemNotification(Base):
    __tablename__ = "system_notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(140))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Draft(Base):
    __tablename__ = "drafts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_code: Mapped[str] = mapped_column(String(40))
    payload_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
