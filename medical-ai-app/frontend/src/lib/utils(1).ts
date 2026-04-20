import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const MODULE_OPTIONS = [
  { value: "brain_mri", label: "Brain MRI Segmentation", badge: "MRI", description: "Phân đoạn khối u não trên ảnh MRI" },
  { value: "histopath", label: "Histopathology Classification", badge: "Pathology", description: "Phân loại ảnh mô bệnh học" },
  { value: "wrist_xray", label: "Wrist X-ray Detection", badge: "X-ray", description: "Phát hiện gãy xương / kim loại" },
] as const;

export const MODULE_RESULT_LABELS: Record<string, string> = {
  brain_mri: "Brain MRI",
  histopath: "Histopath",
  wrist_xray: "Wrist X-ray",
};

export const ACCEPT_MAP: Record<string, string> = {
  brain_mri: ".png,.jpg,.jpeg,.nii,.nii.gz,.dcm",
  histopath: ".png,.jpg,.jpeg",
  wrist_xray: ".png,.jpg,.jpeg,.dcm",
};

export function moduleLabel(moduleType: string) {
  return MODULE_OPTIONS.find((item) => item.value === moduleType)?.label ?? moduleType;
}

export function formatModuleType(moduleType: string) {
  if (moduleType === "brain_mri") return "Brain MRI";
  if (moduleType === "histopath") return "Histopath";
  if (moduleType === "wrist_xray") return "Wrist X-ray";
  return moduleType;
}

export function formatStatus(status: string) {
  if (status === "saved") return "Đã lưu";
  if (status === "pending_confirmation") return "Chờ xác nhận";
  if (status === "error") return "Lỗi xử lý";
  if (status === "draft") return "Bản nháp";
  return status;
}

export function formatDateTime(value?: string) {
  if (!value) return "--";
  return new Date(value).toLocaleString("vi-VN");
}

export function formatDate(value?: string) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("vi-VN");
}

export function assetUrl(path?: string | null) {
  if (!path) return "";
  if (path.startsWith("http")) return path;
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
  return `${baseUrl}${path}`;
}
