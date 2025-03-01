import axios from 'axios'
import { handleAPIError } from '../utils/errors'
import { ModelService } from './modelService'
import type { 
  AxiosInstance, 
  InternalAxiosRequestConfig 
} from 'axios'
import type { Project, Activity, DashboardStats } from '@/apps/home/types/dashboard'
import type { ProjectFile, CodeGenerationResponse, AIModel, APIResponse, ProjectData, UndoResponse } from '../types/builder'
import { AI_MODELS } from '../types/builder'

// Constants for API configuration
const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || window.location.origin,
  DEFAULT_HEADERS: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

const api: AxiosInstance = axios.create({
  baseURL: `${API_CONFIG.BASE_URL}/api/v1`,
  withCredentials: true,
  headers: API_CONFIG.DEFAULT_HEADERS,
  timeout: API_CONFIG.TIMEOUT
})

// Update interceptor to handle CSRF token properly
api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  // Only fetch CSRF token for mutation requests
  if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
    if (!document.cookie.includes('csrftoken')) {
      await axios.get(`${API_CONFIG.BASE_URL}/api/v1/csrf/`)
    }
    
    const csrfToken = document.cookie
      .split('; ')
      .find(row => row.startsWith('csrftoken='))
      ?.split('=')[1]

    if (csrfToken && config.headers) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  
  return config
}, (error) => Promise.reject(handleAPIError(error)))

// Add response interceptor
api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config

    // Implement retry logic for network errors or 5xx responses
    if (
      (error.message.includes('Network Error') || 
       (error.response?.status >= 500 && error.response?.status <= 599)) &&
      originalRequest._retry !== API_CONFIG.RETRY_ATTEMPTS
    ) {
      originalRequest._retry = (originalRequest._retry || 0) + 1
      
      // Exponential backoff
      const delay = API_CONFIG.RETRY_DELAY * Math.pow(2, originalRequest._retry - 1)
      await new Promise(resolve => setTimeout(resolve, delay))
      
      return api(originalRequest)
    }

    if (error.response?.status === 401) {
      // Handle authentication errors
      window.location.href = '/login'
    } else if (error.response?.status === 403) {
      console.error('Permission denied:', error.response.data)
    } else if (error.response?.status === 404) {
      console.error('Resource not found:', error.response.data)
    }
    return Promise.reject(handleAPIError(error))
  }
)

export const BuilderAPI = {
  async getProjects(): Promise<Project[]> {
    try {
      const response = await api.get('/project-manager/projects/')
      console.debug('Projects API response:', {
        status: response.status,
        headers: response.headers,
        data: response.data
      })
      
      // Handle both { data: Project[] } and direct Project[] responses
      const projects = response.data?.data || response.data || []
      if (!Array.isArray(projects)) {
        console.error('Invalid projects response format:', {
          data: response.data,
          type: typeof response.data
        })
        return []
      }
      
      return projects
    } catch (error: any) {
      console.error('Error fetching projects:', {
        error,
        status: error.response?.status,
        data: error.response?.data,
        headers: error.response?.headers,
        url: error.config?.url
      })
      throw handleAPIError(error)
    }
  },

  async createProject(projectData: ProjectData): Promise<Project> {
    try {
      // Ensure projectData has required fields
      if (!projectData.name?.trim()) {
        throw new Error('Project name is required')
      }

      const payload = {
        name: projectData.name.trim(),
        description: projectData.description || '',
        // Add any other required fields with defaults
        status: 'active',
        visibility: 'private'
      }

      console.debug('Creating project with payload:', payload)
      
      const response = await api.post('/project-manager/projects/create/', payload)
      console.debug('Create project response:', {
        status: response.status,
        data: response.data,
        headers: response.headers
      })
      
      // Handle different response formats
      const project = response.data?.data || response.data
      
      if (!project || !project.id) {
        console.error('Invalid project response:', {
          response,
          project
        })
        throw new Error('Invalid project data received from server')
      }
      
      return project
    } catch (error: any) {
      console.error('Project creation error:', {
        error,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url,
        message: error.message
      })

      // Handle specific error cases
      if (error.response?.status === 400) {
        throw new Error(error.response.data.message || 'Invalid project data')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to create projects')
      } else if (error.response?.status === 429) {
        throw new Error('Project creation rate limit exceeded. Please try again later.')
      }

      const errorMessage = error.response?.data?.error 
        || error.response?.data?.message 
        || error.message 
        || 'Failed to create project'
      throw new Error(errorMessage)
    }
  },

  async getProject(projectId: string): Promise<Project> {
    try {
      const response = await api.get<APIResponse<Project>>(`/project-manager/projects/${projectId}/`)
      return response.data.data
    } catch (error) {
      console.error('Error fetching project:', error)
      throw handleAPIError(error)
    }
  },

  async updateProject(projectId: string, projectData: Partial<Project>): Promise<Project> {
    try {
      const response = await api.patch<APIResponse<Project>>(`/project-manager/projects/${projectId}/`, projectData)
      return response.data.data
    } catch (error) {
      console.error('Error updating project:', error)
      throw handleAPIError(error)
    }
  },

  async deleteProject(projectId: string): Promise<void> {
    if (!projectId) {
      throw new Error('Project ID is required')
    }

    try {
      console.debug('Deleting project:', { projectId })
      
      const response = await api.delete(`/project-manager/projects/${projectId}/`)
      
      console.debug('Delete project response:', {
        status: response.status,
        data: response.data
      })

      if (response.status !== 204 && response.status !== 200) {
        throw new Error('Unexpected response status: ' + response.status)
      }
    } catch (error: any) {
      console.error('Error deleting project:', {
        projectId,
        error,
        status: error.response?.status,
        data: error.response?.data,
        url: error.config?.url
      })

      // Handle specific error cases
      if (error.response?.status === 404) {
        throw new Error('Project not found')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to delete this project')
      }
      
      const errorMessage = error.response?.data?.error 
        || error.response?.data?.message 
        || error.message 
        || 'Failed to delete project'
      
      throw new Error(errorMessage)
    }
  },

  async getActivities(): Promise<Activity[]> {
    try {
      const response = await api.get<APIResponse<Activity[]>>('/activities/')
      return response.data.data
    } catch (error) {
      console.error('Error fetching activities:', error)
      throw handleAPIError(error)
    }
  },

  async getStats(): Promise<DashboardStats> {
    try {
      const response = await api.get<APIResponse<DashboardStats>>('/dashboard/stats/')
      return response.data.data
    } catch (error) {
      console.error('Error fetching stats:', error)
      throw handleAPIError(error)
    }
  },

  // File management methods
  async getProjectFiles(projectId: string): Promise<ProjectFile[]> {
    try {
      const response = await api.get(`/products/oasis/builder/projects/${projectId}/files/`)
      return response.data.data || response.data || []
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async getFileContent(projectId: string, filePath: string): Promise<{ content: string }> {
    try {
      const response = await api.get(`/products/oasis/builder/projects/${projectId}/files/${filePath}/content/`)
      return response.data.data || response.data || { content: '' }
    } catch (error) {
      console.error('Error fetching file content:', error)
      throw handleAPIError(error)
    }
  },

  async updateFileContent(projectId: string, filePath: string, content: string): Promise<void> {
    try {
      await api.put(`/products/oasis/builder/projects/${projectId}/files/${filePath}/content/`, { content })
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async createFile(projectId: string, fileData: { name: string, type: string, content: string }): Promise<ProjectFile> {
    try {
      const response = await api.post(`/products/oasis/builder/projects/${projectId}/files/`, fileData)
      return response.data.data || response.data
    } catch (error) {
      console.error('Error creating file:', error)
      throw handleAPIError(error)
    }
  },

  // Component tree and code generation
  async getComponentTree(projectId: string): Promise<any[]> {
    try {
      const response = await api.get<APIResponse<any[]>>(`/project-manager/projects/${projectId}/components/`)
      return response.data.data
    } catch (error) {
      console.error('Error fetching component tree:', error)
      throw handleAPIError(error)
    }
  },

  async generateCode(projectId: string, data: {
    prompt: string;
    mode: string;
    model: string | null;
    file_path?: string;
  }): Promise<CodeGenerationResponse> {
    if (!data.model) {
      throw new Error('AI model must be selected')
    }

    // Check rate limits before making request
    await ModelService.checkRateLimit(data.model)

    // Validate prompt length against model context window
    const config = ModelService.getConfig({ id: data.model } as AIModel)
    const estimatedTokens = ModelService.estimateTokens(data.prompt)
    
    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Prompt is too long for selected model. Please reduce length or choose a different model.`)
    }

    try {
      const response = await api.post(`/products/oasis/builder/projects/${projectId}/generate/`, {
        ...data,
        model_id: data.model
      })
      return response.data
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async processChat(projectId: string, data: {
    prompt: string;
    model: string;
  }): Promise<{
    response: string;
    messages: any[];
  }> {
    // Check rate limits before making request
    await ModelService.checkRateLimit(data.model)

    // Validate message length
    const config = ModelService.getConfig({ id: data.model } as AIModel)
    const estimatedTokens = ModelService.estimateTokens(data.prompt)
    
    if (estimatedTokens > config.maxTokens) {
      throw new Error(`Message is too long for selected model. Please reduce length or choose a different model.`)
    }

    try {
      const response = await api.post('/agents/send-message/', {
        ...data,
        project_id: projectId,
        message: data.prompt
      })
      return {
        response: response.data.assistant_message.content,
        messages: [response.data.user_message, response.data.assistant_message]
      }
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async getAvailableModels(): Promise<AIModel[]> {
    try {
      const response = await api.get('/builder/models/')
      return response.data.models || response.data || AI_MODELS
    } catch (error) {
      console.warn('Failed to fetch AI models from API, using defaults:', error)
      return AI_MODELS
    }
  },

  async undoAction(projectId: string): Promise<UndoResponse> {
    try {
      const response = await api.post<APIResponse<UndoResponse>>(`/project-manager/projects/${projectId}/undo/`)
      return response.data.data
    } catch (error) {
      console.error('Error undoing action:', error)
      throw handleAPIError(error)
    }
  }
}

export type BuilderAPIType = typeof BuilderAPI
