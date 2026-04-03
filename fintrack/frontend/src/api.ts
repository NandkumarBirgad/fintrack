import axios from 'axios';

// Create API instance
const api = axios.create({
  // Proxy will forward /auth, /analytics, etc. to backend
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add access token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Optional: handle token refresh logic here in a response interceptor

export default api;
