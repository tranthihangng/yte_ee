import { create } from "zustand";

type CaseState = {
  currentCaseId?: number;
  setCurrentCaseId: (id?: number) => void;
};

export const useCaseStore = create<CaseState>((set) => ({
  currentCaseId: undefined,
  setCurrentCaseId: (id) => set({ currentCaseId: id })
}));
