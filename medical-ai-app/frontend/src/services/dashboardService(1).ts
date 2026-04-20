import { api } from "@/services/api";
import type { DashboardSummary, RecentCase } from "@/types/dashboard";

export async function fetchDashboardSummary(search?: string) {
  const response = await api.get<DashboardSummary>("/dashboard/summary", { params: { search } });
  return response.data;
}

export async function fetchRecentCases(limit = 5) {
  const response = await api.get<{ items: RecentCase[] }>("/dashboard/recent-cases", { params: { limit } });
  return response.data.items;
}

export async function fetchNotifications(limit = 5) {
  const response = await api.get<{ items: DashboardSummary["notifications"] }>("/dashboard/notifications", { params: { limit } });
  return response.data.items;
}
