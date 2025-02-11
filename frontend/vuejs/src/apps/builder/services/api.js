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
      const response = await api.get('/project-manager/projects/');
      return response.data;
    } catch (error) {
      console.error('Error fetching projects:', error);
      throw error;
    }
  },

  async createProject(projectData) {
    try {
      const response = await api.post('/project-manager/projects/create/', projectData);
      console.log('API Response:', response.data);
      
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid response from server');
      }
      
      return response.data;
    } catch (error) {
      console.error('Error creating project:', error.response?.data || error);
      throw error.response?.data?.error ? new Error(error.response.data.error) : error;
    }
  },

  async getProject(projectId) {
    try {
      const response = await api.get(`/project-manager/projects/${projectId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching project:', error);
      throw error;
    }
  },

  async updateProject(projectId, projectData) {
    try {
      const response = await api.patch(`/project-manager/projects/${projectId}/`, projectData);
      return response.data;
    } catch (error) {
      console.error('Error updating project:', error);
      throw error;
    }
  },

  async deleteProject(projectId) {
    try {
      await api.delete(`/project-manager/projects/${projectId}/delete/`);
    } catch (error) {
      console.error('Error deleting project:', error);
      throw error;
    }
  },

  async getAvailableModels() {
    try {
      const response = await api.get('/builder/models/');
      return response.data;
    } catch (error) {
      console.error('Error fetching available models:', error);
      throw error;
    }
  },

  async getProjectFiles(projectId) {
    try {
      const response = await api.get(`/project-manager/projects/${projectId}/files/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching project files:', error);
      throw error;
    }
  },

  async getFileContent(projectId, filePath) {
    try {
      const response = await api.get(`/project-manager/projects/${projectId}/files/${filePath}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching file content:', error);
      throw error;
    }
  },

  async updateFileContent(projectId, filePath, content) {
    try {
      const response = await api.patch(`/project-manager/projects/${projectId}/files/${filePath}/`, {
        content
      });
      return response.data;
    } catch (error) {
      console.error('Error updating file content:', error);
      throw error;
    }
  },

  async createFile(projectId, fileData) {
    try {
      const response = await api.post(`/project-manager/projects/${projectId}/files/`, fileData);
      return response.data;
    } catch (error) {
      console.error('Error creating file:', error);
      throw error;
    }
  },

  async getComponentTree(projectId) {
    try {
      const response = await api.get(`/project-manager/projects/${projectId}/components/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching component tree:', error);
      throw error;
    }
  },

  async undoAction(projectId, actionId) {
    try {
      const response = await api.post(`/project-manager/projects/${projectId}/undo/${actionId}/`);
      return response.data;
    } catch (error) {
      console.error('Error undoing action:', error);
      throw error;
    }
  }
};