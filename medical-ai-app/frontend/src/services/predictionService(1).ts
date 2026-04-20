import { api } from "@/services/api";
import type { PredictionResponse } from "@/types/prediction";

export interface PredictPayload {
  moduleType: string;
  file: File;
  caseCode: string;
  patientName: string;
  patientIdentifier: string;
  studyDate: string;
  notes: string;
  confidenceThreshold: number;
  saveToHistory: boolean;
  exportReport: boolean;
}

export async function runPrediction(payload: PredictPayload) {
  const formData = new FormData();
  formData.append("file", payload.file);
  formData.append("case_code", payload.caseCode);
  formData.append("patient_name", payload.patientName);
  formData.append("patient_identifier", payload.patientIdentifier);
  formData.append("study_date", payload.studyDate);
  formData.append("notes", payload.notes);
  formData.append("confidence_threshold", String(payload.confidenceThreshold));
  formData.append("save_to_history", String(payload.saveToHistory));
  formData.append("export_report", String(payload.exportReport));

  const endpointMap: Record<string, string> = {
    brain_mri: "/predict/brain-mri",
    histopath: "/predict/histopath",
    wrist_xray: "/predict/wrist-xray",
  };

  const response = await api.post<PredictionResponse>(endpointMap[payload.moduleType], formData);
  return response.data;
}
