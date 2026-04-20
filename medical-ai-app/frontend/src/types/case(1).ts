export type ModuleType = "brain_mri" | "histopath" | "wrist_xray";

export interface LatestPrediction {
  predicted_label?: string | null;
  confidence?: number | null;
  summary?: string | null;
  metrics?: Record<string, unknown>;
  artifacts?: Record<string, string>;
  created_at?: string | null;
}

export interface CaseItem {
  id: number;
  case_code: string;
  patient_name: string;
  patient_identifier: string;
  study_date?: string | null;
  module_type: ModuleType;
  input_file_path: string;
  status: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  latest_prediction?: LatestPrediction | null;
}

export interface CaseListResponse {
  items: CaseItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface DraftRecord {
  id: number;
  case_id?: number | null;
  module_type: string;
  payload: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}
