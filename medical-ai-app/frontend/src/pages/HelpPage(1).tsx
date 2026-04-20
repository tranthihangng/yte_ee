import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function HelpPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-[28px] font-bold text-slate-900">Trợ giúp</h1>
      <Card>
        <CardHeader><CardTitle>Hướng dẫn tích hợp mô hình AI</CardTitle></CardHeader>
        <CardContent className="space-y-3 text-sm leading-7 text-slate-700">
          <p>1. Thay code trong các file predictor tại backend/app/ml/brain_mri, histopath, wrist_xray.</p>
          <p>2. Giữ nguyên interface load_model() và predict(file_path, confidence_threshold) để frontend không cần sửa.</p>
          <p>3. Ảnh kết quả cần được lưu ra outputs và trả về đúng public path dạng /outputs/...</p>
          <p>4. Nếu model cần GPU hoặc package riêng, hãy thêm vào requirements.txt của backend.</p>
          <p>5. Có thể mở rộng FastAPI để thêm xác thực, người dùng, hoặc PostgreSQL khi triển khai production.</p>
        </CardContent>
      </Card>
    </div>
  );
}
