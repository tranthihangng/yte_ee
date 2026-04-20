from datetime import date

from app.core.database import Base, SessionLocal, engine
from app.models.db_case import Case, PredictionResult, SystemNotification
from app.models.db_report import Report
from app.models.db_user import User


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(User).count() == 0:
        db.add(User())
    if db.query(Case).count() == 0:
        case = Case(
            case_code="CA00124",
            patient_name="BN-001",
            patient_identifier="BN1987.001",
            study_date=date.today(),
            module_type="brain_mri",
            input_file_path="uploads/sample_mri.png",
            status="Đã lưu",
        )
        db.add(case)
        db.flush()
        db.add(
            PredictionResult(
                case_id=case.id,
                predicted_label="U não vùng trán",
                confidence=0.94,
                summary="Tổn thương nghi ngờ ác tính",
                metrics_json='{"dice":0.891,"area_cm2":18.37}',
                artifacts_json='{"original_image":"/uploads/sample_mri.png"}',
                raw_output_json='{}',
            )
        )
        db.add(Report(case_id=case.id))
    if db.query(SystemNotification).count() == 0:
        db.add(SystemNotification(title="Cập nhật mô hình", content="Histopathology v2.1.0 đã kích hoạt"))
    db.commit()
    db.close()
    print("Database initialized.")


if __name__ == "__main__":
    run()
