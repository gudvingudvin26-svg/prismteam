import axios from 'axios';

const getBaseUrl = () => {
  if (window.location.hostname.includes('onrender.com')) {
    return 'https://prismteam-backend.onrender.com';
  }
  return '';
};

const BASE_URL = getBaseUrl();

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry && !originalRequest.url?.includes('/auth/')) {
      originalRequest._retry = true;
      try {
        await axios.post(`${BASE_URL}/api/auth/refresh/`, {}, { withCredentials: true });
        return api(originalRequest);
      } catch (refreshError) {
        if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
          window.location.href = '/login';
        }
      }
    }

    if (error.response?.status === 404 && !window.location.pathname.includes('/not-found')) {
      window.location.href = '/not-found';
    }
    if (error.response?.status === 403 && !window.location.pathname.includes('/access-denied')) {
      window.location.href = '/access-denied';
    }

    return Promise.reject(error);
  }
);

export default api;