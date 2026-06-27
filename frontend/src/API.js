import axios from 'axios';
import Cookies from 'js-cookie';

// const api = axios.create({ baseURL: "https://job-agg-backend.vercel.app/" });
const api = axios.create({ baseURL: "http://127.0.0.1:5000/" });

// Add JWT token to all requests if present
api.interceptors.request.use(config => {
  const token = Cookies.get('token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default api;