export interface PredictionResponse {
  module: string;
  predicted_label: string;
  confidence: number;
  metrics: Record<string, unknown>;
  artifacts: Record<string, string>;
  summary: string;
  case_id?: number | null;
  case_code?: string | null;
  status?: string | null;
  report_id?: number | null;
  created_at?: string | null;
}
