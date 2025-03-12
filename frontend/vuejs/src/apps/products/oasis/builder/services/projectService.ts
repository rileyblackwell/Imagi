import api from './api'
import { handleAPIError } from '../utils/errors'
import type { Project, Activity, DashboardStats } from '@/apps/home/types/dashboard'
import type { ProjectFile, APIResponse, ProjectData } from '../types/builder'

/**
 * Service for handling project-related API calls
 */
export const ProjectService = {
  // Project management methods - using ProjectManager API
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
      return response.data.data || response.data
    } catch (error) {
      console.error('Error fetching project:', error)
      throw handleAPIError(error)
    }
  },

  async updateProject(projectId: string, projectData: Partial<Project>): Promise<Project> {
    try {
      const response = await api.patch<APIResponse<Project>>(`/project-manager/projects/${projectId}/`, projectData)
      return response.data.data || response.data
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
      
      const response = await api.delete(`/project-manager/projects/${projectId}/delete/`)
      
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

  // File management methods - using ProjectManager API
  async getProjectFiles(projectId: string): Promise<ProjectFile[]> {
    try {
      const response = await api.get(`/project-manager/projects/${projectId}/files/`)
      return response.data.data || response.data || []
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async getFileContent(projectId: string, filePath: string): Promise<{ content: string }> {
    try {
      const response = await api.get(`/project-manager/projects/${projectId}/files/${filePath}/`)
      return response.data.data || response.data || { content: '' }
    } catch (error) {
      console.error('Error fetching file content:', error)
      throw handleAPIError(error)
    }
  },

  async updateFileContent(projectId: string, filePath: string, content: string): Promise<void> {
    try {
      await api.put(`/project-manager/projects/${projectId}/files/${filePath}/`, { content })
    } catch (error) {
      throw handleAPIError(error)
    }
  },

  async createFile(projectId: string, fileData: { name: string, type: string, content: string }): Promise<ProjectFile> {
    try {
      const response = await api.post(`/project-manager/projects/${projectId}/files/`, fileData)
      return response.data.data || response.data
    } catch (error) {
      console.error('Error creating file:', error)
      throw handleAPIError(error)
    }
  },

  // Component tree
  async getComponentTree(projectId: string): Promise<any[]> {
    try {
      const response = await api.get<APIResponse<any[]>>(`/project-manager/projects/${projectId}/components/`)
      return response.data.data || response.data || []
    } catch (error) {
      console.error('Error fetching component tree:', error)
      throw handleAPIError(error)
    }
  },

  // Dashboard data
  async getActivities(): Promise<Activity[]> {
    try {
      const response = await api.get<APIResponse<Activity[]>>('/project-manager/activities/')
      return response.data.data || response.data || []
    } catch (error) {
      console.error('Error fetching activities:', error)
      throw handleAPIError(error)
    }
  },

  async getStats(): Promise<DashboardStats> {
    try {
      const response = await api.get<APIResponse<DashboardStats>>('/project-manager/stats/')
      return response.data.data || response.data || {
        activeBuildCount: 0,
        apiCallCount: 0,
        creditsUsed: 0
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
      throw handleAPIError(error)
    }
  }
} 