import { api } from "./api";

const cleanParams = (params: Record<string, string | number>) =>
  Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== "" && value !== null && value !== undefined)
  );

export const caseService = {
  getCases: (params: Record<string, string | number>) =>
    api.get("/cases", { params: cleanParams(params) }).then((r) => r.data),
  getCaseById: (caseId: number) => api.get(`/cases/${caseId}`).then((r) => r.data),
  exportCsv: (params: Record<string, string | number>) =>
    api.get("/cases/export-csv", { params: cleanParams(params), responseType: "blob" }).then((r) => r.data)
};
