from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parents[1]
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Case, CaseStatus, ModuleType, Report, SystemNotification, User  # noqa: E402
from app.services.case_service import CaseService  # noqa: E402
from app.services.prediction_service import PredictionService  # noqa: E402
from app.services.report_service import ReportService  # noqa: E402
from app.schemas.report import ReportGenerateRequest  # noqa: E402

SAMPLE_FILES = {
    "brain_mri": "sample_mri.png",
    "histopath": "sample_histopath.png",
    "wrist_xray": "sample_wrist.png",
}


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() == 0:
        db.add(User(full_name="Nguyễn Thị An", email="nguyen.thi.an@example.com", role="Bác sĩ / Quản trị viên", initials="NT"))

    notifications = [
        ("Cập nhật mô hình Histopathology", "08:00 - Hệ thống đã cập nhật phiên bản mô hình Histopathology v2.1.0", "success"),
        ("Sao lưu dữ liệu hoàn tất", "Hôm qua 17:30 - Sao lưu dữ liệu hoàn tất", "info"),
        ("Kiểm tra định kỳ", "Hệ thống chạy kiểm tra định kỳ lúc 22:00 mỗi ngày", "warning"),
    ]
    if db.query(SystemNotification).count() == 0:
        for title, description, level in notifications:
            db.add(SystemNotification(title=title, description=description, level=level))

    db.commit()

    if db.query(Case).count() == 0:
        today = date.today()
        sample_cases = [
            ("CA00124", "BN-001", "Nam - 45 tuổi", "brain_mri"),
            ("CA00125", "BN-002", "Nữ - 62 tuổi", "histopath"),
            ("CA00126", "BN-003", "Nam - 28 tuổi", "wrist_xray"),
            ("CA00127", "BN-004", "Nữ - 55 tuổi", "brain_mri"),
            ("CA00128", "BN-005", "Nam - 17 tuổi", "histopath"),
            ("CA00129", "BN-006", "Nữ - 40 tuổi", "wrist_xray"),
            ("CA00130", "BN-007", "Nam - 71 tuổi", "brain_mri"),
            ("CA00131", "BN-008", "Nữ - 33 tuổi", "histopath"),
        ]
        for idx, (case_code, pid, pname, module_type) in enumerate(sample_cases):
            file_path = str(Path(__file__).resolve().parents[1] / "uploads" / SAMPLE_FILES[module_type])
            case = CaseService.upsert_case(
                db,
                case_code=case_code,
                patient_name=pname,
                patient_identifier=pid,
                study_date=today,
                module_type=module_type,
                input_file_path=file_path,
                status=CaseStatus.SAVED if idx not in {2, 6} else CaseStatus.PENDING_CONFIRMATION,
                notes="Hình ảnh cho thấy tổn thương cần được đối chiếu thêm với lâm sàng trước khi kết luận cuối cùng.",
            )
            prediction = PredictionService.predict(module_type, file_path, 0.8)
            if idx == 3:
                prediction["confidence"] = 0.89
                prediction["predicted_label"] = "Xuất huyết dưới nhện"
                case.status = CaseStatus.ERROR
            if idx == 1:
                prediction["predicted_label"] = "Lungaca1"
            if idx == 4:
                prediction["predicted_label"] = "Adenocarcinoma"
            if idx == 5:
                prediction["predicted_label"] = "Normal"
                prediction["confidence"] = 0.98
            if idx == 6:
                prediction["predicted_label"] = "Thoái hóa chất trắng"
                prediction["confidence"] = 0.86
            if idx == 7:
                prediction["predicted_label"] = "Benign"
            CaseService.attach_prediction(db, case, prediction)
            case.created_at = datetime.utcnow() - timedelta(hours=(8 - idx))
            case.updated_at = case.created_at
            db.commit()

            if idx < 4:
                report = ReportService.create_report_record(db, case, ReportGenerateRequest())
                ReportService.generate_pdf(db, case, report)

    db.close()
    print("Đã seed dữ liệu mẫu.")


if __name__ == "__main__":
    seed()
