import axios from 'axios'

// Ignore extension disconnection errors in console
const originalConsoleError = console.error;
console.error = (...args) => {
  const errorMessage = args.join(' ');
  if (
    errorMessage.includes('runtime.lastError') ||
    errorMessage.includes('extension port') ||
    errorMessage.includes('message port closed') ||
    errorMessage.includes('receiving end does not exist')
  ) {
    return; // Ignore these errors
  }
  originalConsoleError.apply(console, args);
};

const BASE_URL = '/api'

// Add axios interceptor to handle extension errors
axios.interceptors.response.use(
  response => response,
  error => {
    // Ignore extension-related errors
    if (
      error.message?.includes('runtime.lastError') ||
      error.message?.includes('extension port') ||
      error.message?.includes('message port closed') ||
      error.message?.includes('receiving end does not exist')
    ) {
      return Promise.resolve({ data: null }); // Return empty response
    }
    return Promise.reject(error);
  }
);

export const BuilderAPI = {
  // Project endpoints
  async getProjects() {
    const response = await axios.get(`${BASE_URL}/builder/projects/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async createProject(projectData) {
    const response = await axios.post(`${BASE_URL}/builder/projects/`, projectData, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async getProject(id) {
    const response = await axios.get(`${BASE_URL}/builder/projects/${id}/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async updateProject(id, projectData) {
    const response = await axios.patch(`${BASE_URL}/builder/projects/${id}/`, projectData, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async deleteProject(id) {
    const response = await axios.delete(`${BASE_URL}/builder/projects/${id}/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  // File management endpoints
  async getProjectFiles(projectId) {
    const response = await axios.get(`${BASE_URL}/builder/projects/${projectId}/files/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  async createFile(projectId, fileData) {
    const response = await axios.post(`${BASE_URL}/builder/projects/${projectId}/files/`, fileData, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async getFileContent(projectId, filePath) {
    const response = await axios.get(`${BASE_URL}/builder/projects/${projectId}/files/${encodeURIComponent(filePath)}/content/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  async updateFileContent(projectId, filePath, content) {
    const response = await axios.put(`${BASE_URL}/builder/projects/${projectId}/files/${encodeURIComponent(filePath)}/`, {
      content
    }, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  // Component tree endpoints
  async getComponentTree(projectId) {
    const response = await axios.get(`${BASE_URL}/builder/projects/${projectId}/components/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  // AI model endpoints
  async getAvailableModels() {
    const response = await axios.get(`${BASE_URL}/builder/models/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return { models: response.data }
  },

  async generateCode(projectId, data) {
    const response = await axios.post(`${BASE_URL}/builder/projects/${projectId}/generate/`, {
      prompt: data.prompt,
      model: data.model,
      file_path: data.file,
      mode: data.mode
    }, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async undoAction(projectId, actionId) {
    const response = await axios.post(`${BASE_URL}/builder/projects/${projectId}/undo/`, {
      action_id: actionId
    }, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  }
} 