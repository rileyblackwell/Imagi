import axios from 'axios'

const BASE_URL = '/api/builder'

export const BuilderAPI = {
  // Project endpoints
  async getProjects() {
    const response = await axios.get(`${BASE_URL}/projects/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async createProject(projectData) {
    const response = await axios.post(`${BASE_URL}/projects/`, projectData, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async getProject(id) {
    const response = await axios.get(`${BASE_URL}/projects/${id}/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async updateProject(id, projectData) {
    const response = await axios.patch(`${BASE_URL}/projects/${id}/`, projectData, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async deleteProject(id) {
    const response = await axios.delete(`${BASE_URL}/projects/${id}/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  // File management endpoints
  async getProjectFiles(projectId) {
    const response = await axios.get(`${BASE_URL}/projects/${projectId}/files/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  async createFile(projectId, fileData) {
    const response = await axios.post(`${BASE_URL}/projects/${projectId}/files/`, fileData, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async getFileContent(projectId, filePath) {
    const response = await axios.get(`${BASE_URL}/projects/${projectId}/files/${encodeURIComponent(filePath)}/content/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  async updateFileContent(projectId, filePath, content) {
    const response = await axios.put(`${BASE_URL}/projects/${projectId}/files/${encodeURIComponent(filePath)}/`, {
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
    const response = await axios.get(`${BASE_URL}/projects/${projectId}/components/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  // AI model endpoints
  async getAvailableModels() {
    const response = await axios.get(`${BASE_URL}/models/`, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json'
      }
    })
    return response.data
  },

  async generateCode(projectId, options) {
    const response = await axios.post(`${BASE_URL}/projects/${projectId}/generate/`, options, {
      withCredentials: true,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    })
    return response.data
  },

  async undoAction(projectId, actionId) {
    const response = await axios.post(`${BASE_URL}/projects/${projectId}/undo/`, {
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