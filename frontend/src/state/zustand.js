// src/store/useAppStore.js
import { create } from 'zustand';

const useAppStore = create((set) => ({
  loading: false,
  setLoading: (value) => set({ loading: value }),

  // Add more states and actions as needed
  someData: null,
  setSomeData: (data) => set({ someData: data }),

  
}));

export default useAppStore;
