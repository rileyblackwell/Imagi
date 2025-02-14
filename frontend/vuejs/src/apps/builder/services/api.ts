import axios from 'axios'
import type { 
  AxiosInstance, 
  AxiosRequestConfig, 
  InternalAxiosRequestConfig 
} from 'axios'
import type { Project, Activity, DashboardStats } from '@/apps/home/types/dashboard'
import type { ProjectFile, CodeGenerationResponse, AIModel } from '../types/builder'
import { DEFAULT_AI_MODELS } from '../types/builder'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface APIResponse<T> {
  data: T;
  message?: string;
  status: number;
}

interface ProjectData {
  name: string;
  description?: string;
  // Add other project creation fields
}

interface FileData {
  path: string;
  content: string;
  type?: string;
}

interface UndoResponse {
  type: 'file' | 'component' | 'other'
  message: string
}

const api: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  withCredentials: true,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})

// Update interceptor to use InternalAxiosRequestConfig
api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  if (!document.cookie.includes('csrftoken')) {
    await axios.get(`${API_BASE_URL}/api/v1/csrf/`)
  }
  
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1]

  if (csrfToken && config.headers) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  
  return config
})

export const BuilderAPI = {
  async getProjects(): Promise<Project[]> {
    try {
      const response = await api.get('/project-manager/projects/')
      console.debug('Projects API response:', response.data)
      
      // Handle both { data: Project[] } and direct Project[] responses
      const projects = response.data?.data || response.data || []
      if (!Array.isArray(projects)) {
        console.error('Invalid projects response format:', response.data)
        return []
      }
      
      return projects
    } catch (error) {
      console.error('Error fetching projects:', error)
      throw error
    }
  },

  async createProject(projectData: ProjectData): Promise<Project> {
    try {
      const response = await api.post('/project-manager/projects/create/', projectData)
      console.debug('Create project response:', response)
      
      // Handle different response formats
      const project = response.data?.data || response.data
      
      if (!project || !project.id) {
        console.error('Invalid project response:', response)
        throw new Error('Invalid project data received from server')
      }
      
      return project
    } catch (error: any) {
      console.error('Project creation error:', {
        error,
        response: error.response,
        data: error.response?.data
      })
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
      throw error
    }
  },

  async updateProject(projectId: string, projectData: Partial<Project>): Promise<Project> {
    try {
      const response = await api.patch<APIResponse<Project>>(`/project-manager/projects/${projectId}/`, projectData)
      return response.data.data
    } catch (error) {
      console.error('Error updating project:', error)
      throw error
    }
  },

  async deleteProject(projectId: string): Promise<void> {
    try {
      const response = await api.delete(`/project-manager/projects/${projectId}/delete/`);
      
      if (response.status !== 204 && response.status !== 200) {
        throw new Error('Unexpected response status: ' + response.status);
      }
    } catch (error: any) {
      console.error('Error deleting project:', {
        projectId,
        error,
        response: error.response,
        data: error.response?.data
      });
      
      const errorMessage = error.response?.data?.error 
        || error.response?.data?.message 
        || error.message 
        || 'Failed to delete project';
      
      throw new Error(errorMessage);
    }
  },

  async getActivities(): Promise<Activity[]> {
    const response = await api.get<APIResponse<Activity[]>>('/activities/')
    return response.data.data
  },

  async getStats(): Promise<DashboardStats> {
    const response = await api.get<APIResponse<DashboardStats>>('/dashboard/stats/')
    return response.data.data
  },

  // New methods for file management
  async getProjectFiles(projectId: string): Promise<ProjectFile[]> {
    const response = await api.get<APIResponse<ProjectFile[]>>(`/project-manager/projects/${projectId}/files/`)
    return response.data.data
  },

  async getFileContent(projectId: string, filePath: string): Promise<{ content: string }> {
    const response = await api.get<APIResponse<{ content: string }>>(`/project-manager/projects/${projectId}/files/${filePath}/content/`)
    return response.data.data
  },

  async updateFileContent(projectId: string, filePath: string, content: string): Promise<void> {
    await api.put(`/project-manager/projects/${projectId}/files/${filePath}/content/`, { content })
  },

  async createFile(projectId: string, fileData: { name: string, type: string, content: string }): Promise<ProjectFile> {
    const response = await api.post<APIResponse<ProjectFile>>(`/project-manager/projects/${projectId}/files/`, fileData)
    return response.data.data
  },

  // Component tree and code generation
  async getComponentTree(projectId: string): Promise<any[]> {
    const response = await api.get<APIResponse<any[]>>(`/project-manager/projects/${projectId}/components/`)
    return response.data.data
  },

  async generateCode(projectId: string, data: {
    prompt: string
    mode: string
    model: string | null
    file?: string
  }): Promise<CodeGenerationResponse> {
    const response = await api.post<APIResponse<CodeGenerationResponse>>(`/project-manager/projects/${projectId}/generate/`, data)
    return response.data.data
  },

  async getAvailableModels(): Promise<AIModel[]> {
    try {
      const response = await api.get<APIResponse<AIModel[]>>('/ai/models/')
      return response.data.data
    } catch (error) {
      console.warn('Failed to fetch AI models from API, using defaults:', error)
      return DEFAULT_AI_MODELS
    }
  },

  async undoAction(projectId: string): Promise<UndoResponse> {
    const response = await api.post<APIResponse<UndoResponse>>(`/project-manager/projects/${projectId}/undo/`)
    return response.data.data
  }
}

export type BuilderAPIType = typeof BuilderAPI
