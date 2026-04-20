export function SettingsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Cài đặt</h1>
      <div className="card p-5 grid grid-cols-2 gap-4 text-sm">
        <label>Theme<select className="w-full rounded-xl border p-2"><option>Light</option></select></label>
        <label>Ngưỡng mặc định<input className="w-full rounded-xl border p-2" defaultValue="0.8" /></label>
        <label>Thư mục output<input className="w-full rounded-xl border p-2" defaultValue="outputs/" /></label>
        <label>Tên hệ thống<input className="w-full rounded-xl border p-2" defaultValue="MedAI Assist" /></label>
      </div>
    </div>
  );
}
