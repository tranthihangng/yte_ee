export interface ReportRecord {
  id: number;
  case_id: number;
  template_type: string;
  include_images: boolean;
  include_metrics: boolean;
  include_notes: boolean;
  mask_personal_info: boolean;
  pdf_path: string;
  created_at: string;
}

export interface ReportResponse {
  report: ReportRecord;
  case: {
    id: number;
    case_code: string;
    patient_name: string;
    patient_identifier: string;
    study_date: string;
    module_type: string;
    status: string;
    notes: string;
    input_file_path: string;
  };
  prediction?: {
    predicted_label: string;
    confidence: number;
    summary: string;
    metrics: Record<string, unknown>;
    artifacts: Record<string, string>;
    created_at: string;
  } | null;
}
