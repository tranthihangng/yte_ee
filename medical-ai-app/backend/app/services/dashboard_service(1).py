from __future__ import annotations

import json
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Case, ModuleType, PredictionResult, SystemNotification


class DashboardService:
    @staticmethod
    def get_summary(db: Session, search: str | None = None) -> dict:
        total_cases = int(db.execute(select(func.count(Case.id))).scalar() or 0)
        today_cases = int(
            db.execute(
                select(func.count(Case.id)).where(func.date(Case.created_at) == date.today())
            ).scalar()
            or 0
        )
        confidences = db.execute(select(PredictionResult.confidence)).scalars().all()
        average_accuracy = round((sum(confidences) / len(confidences) * 100) if confidences else 0.0, 1)
        active_modules = len(ModuleType)

        performance = {
            "dice": 0.891,
            "accuracy": 0.948,
            "confidence": 0.926,
        }

        matches = []
        if search:
            like = f"%{search}%"
            search_stmt = (
                select(Case)
                .where(Case.case_code.ilike(like))
                .order_by(Case.created_at.desc())
                .limit(6)
            )
            matches = [
                {"id": c.id, "case_code": c.case_code, "module_type": c.module_type.value}
                for c in db.execute(search_stmt).scalars().all()
            ]

        notifications = DashboardService.list_notifications(db)
        return {
            "total_cases": total_cases,
            "today_cases": today_cases,
            "average_accuracy": average_accuracy,
            "active_modules": active_modules,
            "search_matches": matches,
            "performance": performance,
            "quick_tips": [
                "Bạn có thể kéo thả ảnh trực tiếp vào trang “Phân tích mới” để bắt đầu phân tích nhanh chóng.",
                "Xem báo cáo hiệu suất định kỳ giúp theo dõi chất lượng mô hình và cải thiện độ chính xác.",
            ],
            "notifications": notifications,
        }

    @staticmethod
    def recent_cases(db: Session, limit: int = 5) -> list[dict]:
        stmt = select(Case).order_by(Case.created_at.desc()).limit(limit)
        cases = db.execute(stmt).scalars().all()
        items = []
        for case in cases:
            prediction = None
            if case.prediction_results:
                prediction = sorted(case.prediction_results, key=lambda x: x.created_at)[-1]
            items.append(
                {
                    "id": case.id,
                    "case_code": case.case_code,
                    "module_type": case.module_type.value,
                    "created_at": case.created_at,
                    "predicted_label": prediction.predicted_label if prediction else None,
                    "status": case.status.value,
                    "confidence": round(prediction.confidence, 2) if prediction else None,
                }
            )
        return items

    @staticmethod
    def list_notifications(db: Session, limit: int = 4) -> list[dict]:
        stmt = select(SystemNotification).order_by(SystemNotification.created_at.desc()).limit(limit)
        rows = db.execute(stmt).scalars().all()
        return [
            {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "level": row.level,
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]
