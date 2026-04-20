export type CaseRecord = {
  id: number;
  case_code: string;
  patient_name: string;
  patient_identifier: string;
  study_date: string;
  module_type: string;
  status: string;
  predicted_label?: string;
  confidence?: number;
  created_at: string;
};
