# MedAI Assist — Medical AI Fullstack App

Ứng dụng fullstack production-style để tích hợp 3 mô hình AI phân tích ảnh y tế bằng Python:

- Brain MRI Segmentation
- Histopathology Classification
- Wrist X-ray Detection

Stack chính:

- Frontend: React + Vite + TypeScript
- UI: Tailwind CSS + component layer kiểu shadcn + lucide-react
- State: Zustand
- Router: React Router
- Form: react-hook-form + zod
- Table: tanstack/react-table
- Chart: Recharts
- Backend: FastAPI
- ORM: SQLAlchemy
- DB: SQLite
- PDF: ReportLab

## 1. Cấu trúc dự án

```text
medical-ai-app/
├── backend/
├── frontend/
└── README.md
```

## 2. Chạy backend

Mở terminal 1:

```bash
cd backend
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python -m app.init_db
python -m app.seed
uvicorn app.main:app --reload
```

### macOS / Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m app.init_db
python -m app.seed
uvicorn app.main:app --reload
```

Backend mặc định chạy tại:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## 3. Chạy frontend

Mở terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Frontend mặc định chạy tại:

```text
http://127.0.0.1:5173
```

## 4. Tích hợp model thật

Bạn chỉ cần thay logic trong 3 file sau:

```text
backend/app/ml/brain_mri/predictor.py
backend/app/ml/histopath/predictor.py
backend/app/ml/wrist_xray/predictor.py
```

### Interface bắt buộc

#### Brain MRI

```python
load_model()
predict(file_path: str, confidence_threshold: float = 0.5) -> dict
```

Output:

```python
{
  "module": "brain_mri",
  "predicted_label": "U não vùng trán",
  "confidence": 0.94,
  "metrics": {
    "dice": 0.891,
    "area_cm2": 18.37
  },
  "artifacts": {
    "original_image": "/outputs/...",
    "overlay_image": "/outputs/...",
    "mask_image": "/outputs/..."
  },
  "summary": "Vùng tăng tín hiệu bất thường tại thùy trán phải"
}
```

#### Histopathology

```python
load_model()
predict(file_path: str, confidence_threshold: float = 0.5) -> dict
```

#### Wrist X-ray

```python
load_model()
predict(file_path: str, confidence_threshold: float = 0.5) -> dict
```

## 5. API chính

### Health

- `GET /api/health`

### Dashboard

- `GET /api/dashboard/summary`
- `GET /api/dashboard/recent-cases`
- `GET /api/dashboard/notifications`

### Cases

- `POST /api/cases`
- `GET /api/cases`
- `GET /api/cases/{case_id}`
- `GET /api/cases/export-csv`
- `POST /api/cases/upload`
- `POST /api/cases/drafts`
- `GET /api/cases/drafts/latest`

### Prediction

- `POST /api/predict/brain-mri`
- `POST /api/predict/histopath`
- `POST /api/predict/wrist-xray`

### Reports

- `GET /api/reports/{report_id}`
- `GET /api/reports/case/{case_id}/latest`
- `POST /api/reports/{case_id}/generate-pdf`
- `GET /api/reports/{case_id}/download-pdf`
- `POST /api/reports/{report_id}/send-email`

### Settings

- `GET /api/settings`
- `PUT /api/settings`

## 6. Database

SQLite file sẽ được tạo tại:

```text
backend/medical_ai.db
```

Các bảng:

- users
- cases
- prediction_results
- reports
- system_notifications
- drafts

## 7. Gợi ý thay predictor bằng model thật

### Brain MRI

1. Load model trong `__init__` hoặc `load_model()`
2. Đọc file ảnh / DICOM / NIfTI trong `preprocess.py`
3. Chạy inference
4. Lưu overlay, mask vào `backend/outputs`
5. Trả đúng JSON theo contract

### Histopathology

1. Nhận ảnh RGB
2. Chạy classifier
3. Tạo Grad-CAM thật
4. Lưu ảnh Grad-CAM
5. Trả output JSON

### Wrist X-ray

1. Load detector thật (ví dụ YOLO)
2. Chạy detect
3. Vẽ bbox
4. Lưu ảnh detection
5. Trả output JSON

## 8. Mẹo nâng cấp production

- Đổi SQLite sang PostgreSQL bằng cách sửa `DATABASE_URL`
- Bổ sung auth JWT trong `security.py`
- Dùng Celery / RQ nếu inference nặng
- Thêm Nginx reverse proxy khi deploy
- Thêm S3 / MinIO nếu muốn lưu file tập trung
- Thêm SMTP / Resend / SendGrid cho gửi email báo cáo

## 9. Lưu ý

Bản hiện tại đã chạy được end-to-end với stub predictor thật sự tạo artifact ảnh và PDF, để bạn:

1. chạy backend bằng uvicorn
2. chạy frontend bằng npm run dev
3. upload ảnh thật
4. gọi predictor
5. xem kết quả trên UI
6. lưu lịch sử
7. xem và xuất báo cáo PDF

## 10. Seed data

Sau khi chạy:

```bash
python -m app.seed
```

sẽ có dữ liệu mẫu cho:

- Dashboard
- History
- Reports
- Notifications
