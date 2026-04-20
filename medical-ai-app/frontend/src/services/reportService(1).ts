import { api } from "@/services/api";
import type { ReportResponse } from "@/types/report";

export async function fetchReportById(reportId: number) {
  const response = await api.get<ReportResponse>(`/reports/${reportId}`);
  return response.data;
}

export async function fetchLatestReportByCase(caseId: number) {
  const response = await api.get<ReportResponse>(`/reports/case/${caseId}/latest`);
  return response.data;
}

export async function generateReport(caseId: number, payload: Record<string, unknown>) {
  const response = await api.post<ReportResponse>(`/reports/${caseId}/generate-pdf`, payload);
  return response.data;
}

export function getDownloadPdfUrl(caseId: number) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
  return `${baseUrl}/reports/${caseId}/download-pdf`;
}
