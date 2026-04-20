import { api } from "./api";

export const dashboardService = {
  getSummary: () => api.get("/dashboard/summary").then((r) => r.data),
  getRecentCases: () => api.get("/dashboard/recent-cases").then((r) => r.data)
};
