from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.models import Case, CaseStatus, Draft, ModuleType, PredictionResult
from app.schemas.case import CaseCreate, DraftCreate
from app.utils.export_utils import rows_to_csv_bytes


class CaseService:
    @staticmethod
    def create_case(db: Session, payload: CaseCreate) -> Case:
        case = Case(**payload.model_dump())
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def get_case(db: Session, case_id: int) -> Case | None:
        return db.get(Case, case_id)

    @staticmethod
    def get_case_by_code(db: Session, case_code: str) -> Case | None:
        stmt = select(Case).where(Case.case_code == case_code)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def upsert_case(
        db: Session,
        *,
        case_code: str,
        patient_name: str,
        patient_identifier: str,
        study_date,
        module_type: str,
        input_file_path: str,
        status: CaseStatus,
        notes: str = "",
    ) -> Case:
        case = CaseService.get_case_by_code(db, case_code)
        if case is None:
            case = Case(
                case_code=case_code,
                patient_name=patient_name,
                patient_identifier=patient_identifier,
                study_date=study_date,
                module_type=ModuleType(module_type),
                input_file_path=input_file_path,
                status=status,
                notes=notes,
            )
            db.add(case)
        else:
            case.patient_name = patient_name
            case.patient_identifier = patient_identifier
            case.study_date = study_date
            case.module_type = ModuleType(module_type)
            case.input_file_path = input_file_path
            case.status = status
            case.notes = notes
            case.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def attach_prediction(db: Session, case: Case, prediction: dict) -> PredictionResult:
        row = PredictionResult(
            case_id=case.id,
            predicted_label=prediction["predicted_label"],
            confidence=float(prediction["confidence"]),
            summary=prediction.get("summary", ""),
            metrics_json=json.dumps(prediction.get("metrics", {}), ensure_ascii=False),
            artifacts_json=json.dumps(prediction.get("artifacts", {}), ensure_ascii=False),
            raw_output_json=json.dumps(prediction, ensure_ascii=False),
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return row

    @staticmethod
    def serialize_case(case: Case) -> dict:
        latest = None
        if case.prediction_results:
            pred = sorted(case.prediction_results, key=lambda item: item.created_at)[-1]
            latest = {
                "predicted_label": pred.predicted_label,
                "confidence": pred.confidence,
                "summary": pred.summary,
                "metrics": json.loads(pred.metrics_json or "{}"),
                "artifacts": json.loads(pred.artifacts_json or "{}"),
                "created_at": pred.created_at,
            }
        return {
            "id": case.id,
            "case_code": case.case_code,
            "patient_name": case.patient_name,
            "patient_identifier": case.patient_identifier,
            "study_date": case.study_date,
            "module_type": case.module_type.value if hasattr(case.module_type, "value") else str(case.module_type),
            "input_file_path": case.input_file_path,
            "status": case.status.value if hasattr(case.status, "value") else str(case.status),
            "notes": case.notes,
            "created_at": case.created_at,
            "updated_at": case.updated_at,
            "latest_prediction": latest,
        }

    @staticmethod
    def list_cases(
        db: Session,
        *,
        page: int = 1,
        page_size: int = 8,
        search: str | None = None,
        module_type: str | None = None,
        status: str | None = None,
        date_from=None,
        date_to=None,
    ) -> tuple[list[dict], int]:
        conditions = []

        if search:
            like = f"%{search}%"
            conditions.append(
                or_(
                    Case.case_code.ilike(like),
                    Case.patient_name.ilike(like),
                    Case.patient_identifier.ilike(like),
                )
            )
        if module_type:
            conditions.append(Case.module_type == ModuleType(module_type))
        if status:
            conditions.append(Case.status == CaseStatus(status))
        if date_from:
            conditions.append(Case.study_date >= date_from)
        if date_to:
            conditions.append(Case.study_date <= date_to)

        stmt = select(Case).order_by(Case.created_at.desc())
        count_stmt = select(func.count(Case.id))

        if conditions:
            stmt = stmt.where(and_(*conditions))
            count_stmt = count_stmt.where(and_(*conditions))

        total = int(db.execute(count_stmt).scalar() or 0)
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        cases = db.execute(stmt).scalars().unique().all()
        return [CaseService.serialize_case(case) for case in cases], total

    @staticmethod
    def export_cases_csv(
        db: Session,
        *,
        search: str | None = None,
        module_type: str | None = None,
        status: str | None = None,
        date_from=None,
        date_to=None,
    ) -> bytes:
        items, _ = CaseService.list_cases(
            db,
            page=1,
            page_size=10_000,
            search=search,
            module_type=module_type,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )
        rows = []
        for item in items:
            latest = item.get("latest_prediction") or {}
            rows.append(
                {
                    "Mã ca": item["case_code"],
                    "Bệnh nhân": item["patient_name"],
                    "Mã BN": item["patient_identifier"],
                    "Ngày chụp": item["study_date"] or "",
                    "Mô-đun": item["module_type"],
                    "Kết quả": latest.get("predicted_label", ""),
                    "Độ tin cậy": latest.get("confidence", ""),
                    "Trạng thái": item["status"],
                    "Thời gian tạo": item["created_at"],
                }
            )
        return rows_to_csv_bytes(list(rows[0].keys()) if rows else ["Mã ca"], rows)

    @staticmethod
    def save_draft(db: Session, payload: DraftCreate) -> Draft:
        draft = Draft(case_id=payload.case_id, module_type=payload.module_type, payload_json=json.dumps(payload.payload, ensure_ascii=False))
        db.add(draft)
        db.commit()
        db.refresh(draft)
        return draft

    @staticmethod
    def get_latest_draft(db: Session) -> Draft | None:
        stmt = select(Draft).order_by(Draft.updated_at.desc()).limit(1)
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def serialize_draft(draft: Draft) -> dict:
        return {
            "id": draft.id,
            "case_id": draft.case_id,
            "module_type": draft.module_type,
            "payload": json.loads(draft.payload_json or "{}"),
            "created_at": draft.created_at,
            "updated_at": draft.updated_at,
        }
