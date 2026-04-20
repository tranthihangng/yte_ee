import { create } from "zustand";

type AppState = {
  searchText: string;
  selectedModule: string;
  setSearchText: (value: string) => void;
  setSelectedModule: (value: string) => void;
};

export const useAppStore = create<AppState>((set) => ({
  searchText: "",
  selectedModule: "brain_mri",
  setSearchText: (value) => set({ searchText: value }),
  setSelectedModule: (value) => set({ selectedModule: value }),
}));
