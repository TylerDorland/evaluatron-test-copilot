import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/api/auth/login', new URLSearchParams({ username, password }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }),
  register: (data) => api.post('/api/auth/register', data),
};

// Companies API
export const companiesAPI = {
  list: () => api.get('/api/companies/'),
  get: (id) => api.get(`/api/companies/${id}`),
  create: (data) => api.post('/api/companies/', data),
};

// Topics API
export const topicsAPI = {
  list: () => api.get('/api/topics/'),
  get: (id) => api.get(`/api/topics/${id}`),
  create: (data) => api.post('/api/topics/', data),
};

// Queries API
export const queriesAPI = {
  list: (params) => api.get('/api/queries/', { params }),
  get: (id) => api.get(`/api/queries/${id}`),
  create: (data) => api.post('/api/queries/', data),
};

// Evaluations API
export const evaluationsAPI = {
  create: (data) => api.post('/api/evaluations/', data),
  getForQuery: (queryId) => api.get(`/api/evaluations/query/${queryId}`),
  get: (id) => api.get(`/api/evaluations/${id}`),
};

// Scheduled Tests API
export const scheduledTestsAPI = {
  list: () => api.get('/api/scheduled-tests/'),
  get: (id) => api.get(`/api/scheduled-tests/${id}`),
  create: (data) => api.post('/api/scheduled-tests/', data),
  update: (id, isActive) => api.put(`/api/scheduled-tests/${id}`, null, { params: { is_active: isActive } }),
};

export default api;
