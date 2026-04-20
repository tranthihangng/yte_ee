import { create } from "zustand";
import type { PredictionResponse } from "@/types/prediction";

type CaseStore = {
  currentFile: File | null;
  currentPreview: string;
  currentPrediction: PredictionResponse | null;
  setCurrentFile: (file: File | null, preview: string) => void;
  setCurrentPrediction: (prediction: PredictionResponse | null) => void;
  clear: () => void;
};

export const useCaseStore = create<CaseStore>((set) => ({
  currentFile: null,
  currentPreview: "",
  currentPrediction: null,
  setCurrentFile: (file, preview) => set({ currentFile: file, currentPreview: preview }),
  setCurrentPrediction: (prediction) => set({ currentPrediction: prediction }),
  clear: () => set({ currentFile: null, currentPreview: "", currentPrediction: null }),
}));
