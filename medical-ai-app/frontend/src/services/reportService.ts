import { api } from "./api";

export const reportService = {
  getReport: (reportId: string) => api.get(`/reports/${reportId}`).then((r) => r.data),
  getReportPreview: (caseId: number) => api.get(`/reports/case/${caseId}/preview`).then((r) => r.data),
  generatePdf: (caseId: number, payload: Record<string, unknown>) =>
    api.post(`/reports/${caseId}/generate-pdf`, payload).then((r) => r.data),
  downloadPdf: (caseId: number) =>
    api.get(`/reports/${caseId}/download-pdf`, { responseType: "blob" }).then((r) => r.data)
};
