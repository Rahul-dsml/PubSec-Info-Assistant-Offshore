import axios from 'axios';

// Base Axios Client setup that has the base url of the backend
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_NHC_BACKEND_BASR_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});


// Chat service api
export const chatService = async (user_query,chat_history,chat_language) => {
    const response = await apiClient.post(
      '/users/assistant_chat',
      { user_query,chat_history,chat_language }
    );
    return response.data;
  };

  export const reportService = async (apartment_id,language) => {      
    const response = await apiClient.post(
      '/users/get_details',
      {apartment_id,language }
    );
    return response.data;
  }




