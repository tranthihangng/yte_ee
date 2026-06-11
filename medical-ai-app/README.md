# MedAI Assist - Medical AI Fullstack App

Ứng dụng web fullstack để tích hợp 3 mô hình AI phân tích ảnh y tế (Brain MRI, Histopathology, Wrist X-ray).

## Workflow Git gợi ý

Xem template ngắn để track task và rollback version tại `WORKFLOW.md`.

## 1) Chạy backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
uvicorn app.main:app --reload --port 8000
```
uvicorn app.main:app --host 0.0.0.0 --port 8000


## 2) Chạy frontend

```bash
cd frontend
npm install
npm run dev
```
npm run dev -- --host 0.0.0.0 --port 5173


Frontend chạy tại `http://localhost:5173`, backend tại `http://localhost:8000`.

## 3) API chính

- `GET /api/health`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/recent-cases`
- `POST /api/cases`
- `GET /api/cases`
- `GET /api/cases/{case_id}`
- `POST /api/predict/brain-mri`
- `POST /api/predict/histopath`
- `POST /api/predict/wrist-xray`
- `GET /api/reports/{report_id}`
- `POST /api/reports/{case_id}/generate-pdf`
- `GET /api/reports/{case_id}/download-pdf`
- `GET /api/cases/export-csv`

## 4) Gắn model thật

Bạn chỉ cần thay logic trong:

- `backend/app/ml/brain_mri/predictor.py`
- `backend/app/ml/histopath/predictor.py`
- `backend/app/ml/wrist_xray/predictor.py`

Mỗi predictor giữ nguyên interface:

- `load_model()`
- `predict(file_path: str, confidence_threshold: float = 0.5) -> dict`

### Tích hợp từ mã hiện có của bạn

- X-ray hiện đã map theo workflow `gd/xray/predict.py`:
  - tự load weight `gd/xray/last35.pt`
  - chạy YOLO predict và lưu ảnh bbox vào `backend/outputs/detections`
- MRI hiện đã map theo `gd/mri/predict_brats_2d.py`:
  - cố gắng load CBIM model/config nếu checkpoint có sẵn
  - fallback an toàn khi chưa có checkpoint/dependency
  - xuất `original/overlay/mask` vào `backend/outputs`

## 5) Ghi chú nâng cấp PostgreSQL

Đổi biến `database_url` trong `backend/app/core/config.py` hoặc `.env` sang PostgreSQL URL, SQLAlchemy models giữ nguyên để migrate.

## 6) Cấu hình gửi email báo cáo

Thêm vào `backend/.env`:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true
```

## 7) Đăng nhập bằng file JSON

Tạo file local từ mẫu trước khi chạy backend:

```bash
cp backend/data/users.example.json backend/data/users.json
```

- File `backend/data/users.json` được Git bỏ qua để tránh lộ tài khoản.
- Đổi ngay mật khẩu mẫu trước khi triển khai.
- Hỗ trợ `password` cho local và `password_hash` an toàn hơn.
