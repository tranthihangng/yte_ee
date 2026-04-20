export function HelpPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Trợ giúp</h1>
      <div className="card p-5">
        <ul className="list-disc pl-6 text-sm text-slate-700 space-y-2">
          <li>Chọn đúng module trước khi phân tích.</li>
          <li>Ảnh MRI nên rõ nét, không bị nhiễu nhiều.</li>
          <li>Nếu mô hình lỗi, kiểm tra backend logs và định dạng file.</li>
        </ul>
      </div>
    </div>
  );
}
