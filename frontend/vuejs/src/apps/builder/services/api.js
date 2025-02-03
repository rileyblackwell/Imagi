import axios from 'axios'

const BASE_URL = '/api/builder'

export const BuilderAPI = {
  // Project endpoints
  async listProjects() {
    const response = await axios.get(`${BASE_URL}/projects/`)
    return response.data
  },

  async createProject(name) {
    const response = await axios.post(`${BASE_URL}/projects/`, { name })
    return response.data
  },

  async getProject(id) {
    const response = await axios.get(`${BASE_URL}/projects/${id}/`)
    return response.data
  },

  async deleteProject(id) {
    const response = await axios.delete(`${BASE_URL}/projects/${id}/`)
    return response.data
  },

  // File management endpoints
  async listFiles(projectId) {
    const response = await axios.get(`${BASE_URL}/projects/${projectId}/files/`)
    return response.data
  },

  async getFileContent(projectId, filePath) {
    const response = await axios.get(`${BASE_URL}/projects/${projectId}/files/${filePath}/content/`)
    return response.data.content
  },

  async updateFile(projectId, filePath, content, commitMessage = 'Update file') {
    const response = await axios.put(`${BASE_URL}/projects/${projectId}/files/${filePath}/`, {
      content,
      commit_message: commitMessage
    })
    return response.data
  },

  // AI model endpoints
  async generateCode(projectId, prompt, model = 'claude-3-5-sonnet-20241022', filePath = null) {
    const response = await axios.post(`${BASE_URL}/projects/${projectId}/generate/`, {
      prompt,
      model,
      file_path: filePath
    })
    return response.data
  },

  async getAvailableModels() {
    const response = await axios.get(`${BASE_URL}/models/`)
    return response.data
  },

  async undoLastAction(projectId) {
    const response = await axios.post(`${BASE_URL}/projects/${projectId}/undo/`)
    return response.data
  }
} 