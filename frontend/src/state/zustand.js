// src/store/useAppStore.js
import { create } from 'zustand';

const useAppStore = create((set) => ({


  showRecommendation:false,
  setShowRecommendation:(value)=>set({showRecommendation:value}),

  showReport:false,
  setShowReport:(value)=>set({showReport:value}),

  reportResults:"",
  setReportResults:(data)=>set({reportResults : data}),
  

  showRecommendationCards:false,
  setShowRecommendationCards:(value)=>set({showRecommendationCards:value}),

  latLongDetails:[{}],
  setLatLongDetails:(data)=>set({latLongDetails:data}),

  
  
}));

export default useAppStore;
