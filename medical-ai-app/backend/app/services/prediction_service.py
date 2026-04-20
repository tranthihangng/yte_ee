import json
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.db_case import Case, PredictionResult


def save_prediction(db: Session, case: Case, result: dict) -> PredictionResult:
    prediction = PredictionResult(
        case_id=case.id,
        predicted_label=result["predicted_label"],
        confidence=result["confidence"],
        summary=result["summary"],
        metrics_json=json.dumps(result["metrics"], ensure_ascii=False),
        artifacts_json=json.dumps(result["artifacts"], ensure_ascii=False),
        raw_output_json=json.dumps(result, ensure_ascii=False),
    )
    case.status = "Đã lưu"
    case.updated_at = datetime.utcnow()
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction
