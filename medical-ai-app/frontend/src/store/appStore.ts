import { create } from "zustand";

type AppState = {
  selectedModule: "brain_mri" | "histopath" | "wrist_xray" | "tuberculosis_counting";
  setSelectedModule: (m: AppState["selectedModule"]) => void;
};

export const useAppStore = create<AppState>((set) => ({
  selectedModule: "brain_mri",
  setSelectedModule: (selectedModule) => set({ selectedModule })
}));
