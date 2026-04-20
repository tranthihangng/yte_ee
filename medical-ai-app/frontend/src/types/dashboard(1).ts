export interface DashboardSummary {
  total_cases: number;
  today_cases: number;
  average_accuracy: number;
  active_modules: number;
  search_matches: Array<{ id: number; case_code: string; module_type: string }>;
  performance: {
    dice: number;
    accuracy: number;
    confidence: number;
  };
  quick_tips: string[];
  notifications: Array<{
    id: number;
    title: string;
    description: string;
    level: string;
    created_at: string;
  }>;
}

export interface RecentCase {
  id: number;
  case_code: string;
  module_type: string;
  created_at: string;
  predicted_label?: string | null;
  status: string;
  confidence?: number | null;
}
