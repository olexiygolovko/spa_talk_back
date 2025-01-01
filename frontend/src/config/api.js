import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://spa-talk-back.onrender.com/api'
  : 'http://127.0.0.1:8000/api';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  }
});

axiosInstance.interceptors.request.use(config => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const API_URLS = {
  // Auth endpoints
  LOGIN: `${API_BASE_URL}/login/`,
  REGISTER: `${API_BASE_URL}/register/`,
  
  // Posts endpoints
  POSTS: `${API_BASE_URL}/posts/`,
  POST_DETAIL: (id) => `${API_BASE_URL}/posts/${id}/`,
  
  // Comments endpoints
  COMMENTS: `${API_BASE_URL}/comments/`,
  POST_COMMENTS: (postId) => `${API_BASE_URL}/posts/${postId}/comments/`,
  COMMENT_DETAIL: (id) => `${API_BASE_URL}/comments/${id}/`,
};

export default axiosInstance;
