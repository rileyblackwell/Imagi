import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance
const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  withCredentials: true,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
});

// Add request interceptor to get CSRF token
api.interceptors.request.use(async (config) => {
  // Get CSRF token if we don't have it
  if (!document.cookie.includes('csrftoken')) {
    await axios.get(`${API_BASE_URL}/api/v1/csrf/`);
  }
  
  // Get token from cookies
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken;
  }
  
  return config;
});

export const BuilderAPI = {
  async getProjects() {
    try {
      const response = await api.get('/projects/');
      return response.data;
    } catch (error) {
      console.error('Error fetching projects:', error);
      throw error;
    }
  },

  async createProject(projectData) {
    try {
      const response = await api.post('/projects/', projectData);
      return response.data;
    } catch (error) {
      console.error('Error creating project:', error);
      throw error;
    }
  },

  async getProject(projectId) {
    try {
      const response = await api.get(`/projects/${projectId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching project:', error);
      throw error;
    }
  },

  async deleteProject(projectId) {
    try {
      await api.delete(`/projects/${projectId}/`);
    } catch (error) {
      console.error('Error deleting project:', error);
      throw error;
    }
  }
};