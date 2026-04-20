import { api } from "@/services/api";
import type { CaseItem, CaseListResponse, DraftRecord } from "@/types/case";

export async function fetchCases(params: Record<string, unknown>) {
  const response = await api.get<CaseListResponse>("/cases", { params });
  return response.data;
}

export async function fetchCase(caseId: number) {
  const response = await api.get<CaseItem>(`/cases/${caseId}`);
  return response.data;
}

export async function uploadCaseFile(moduleType: string, file: File) {
  const formData = new FormData();
  formData.append("module_type", moduleType);
  formData.append("file", file);
  const response = await api.post<{ file_path: string; preview_path: string; filename: string }>("/cases/upload", formData);
  return response.data;
}

export async function saveDraft(payload: { case_id?: number | null; module_type: string; payload: Record<string, unknown> }) {
  const response = await api.post<DraftRecord>("/cases/drafts", payload);
  return response.data;
}

export async function fetchLatestDraft() {
  const response = await api.get<{ draft: DraftRecord | null }>("/cases/drafts/latest");
  return response.data.draft;
}

export function getCasesCsvUrl(params: Record<string, string | number | undefined>) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") query.append(key, String(value));
  });
  return `${baseUrl}/cases/export-csv?${query.toString()}`;
}
