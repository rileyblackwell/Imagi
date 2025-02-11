import axios from 'axios'
import type { 
  AxiosInstance, 
  AxiosRequestConfig, 
  InternalAxiosRequestConfig 
} from 'axios'
import type { Project, Activity, DashboardStats } from '@/apps/home/types/dashboard'

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
      await api.delete(`/project-manager/projects/${projectId}/delete/`)
    } catch (error) {
      console.error('Error deleting project:', error)
      throw error
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
}

export type BuilderAPIType = typeof BuilderAPI
