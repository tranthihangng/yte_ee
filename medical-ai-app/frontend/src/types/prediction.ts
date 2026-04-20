export type PredictionResult = {
  module: string;
  predicted_label: string;
  confidence: number;
  summary: string;
  case_id?: number;
  metrics: Record<string, unknown>;
  artifacts: Record<string, string>;
};
