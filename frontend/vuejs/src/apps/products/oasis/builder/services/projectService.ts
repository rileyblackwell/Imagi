import axios from 'axios'
import api from './api'

// Define API path constants
const API_PATHS = {
  PROJECT_MANAGER: 'project-manager',
  BUILDER: 'builder',
  PRODUCTS_OASIS_PROJECT_MANAGER: 'products/oasis/project-manager',
  PRODUCTS_OASIS_BUILDER: 'products/oasis/builder',
  CORE_BUILDER: 'builder',
  DIRECT_BUILDER: 'builder', 
  ABSOLUTE_API: window.location.origin + '/api/v1/project-manager' // Updated to use project-manager
}

// Define cache keys
const CACHE_KEYS = {
  PROJECTS: 'imagi_cached_projects',
  PROJECT_PREFIX: 'imagi_project_'
}

import type { Project } from '../types/project'
import type { ProjectFile } from '../types/builder'
import type { Activity, DashboardStats } from '@/apps/home/types/dashboard'

/**
 * Project Service
 * 
 * This service handles communication with the backend API for:
 * 1. Project Management (create, update, delete, list) - Dashboard
 * 2. Project File Operations (create, edit, delete) - Workspace
 * 
 * Functions are separated into these two categories to maintain clear boundaries.
 */
export const ProjectService = {
  // Cache management helpers
  _getCachedProjects() {
    try {
      const cached = localStorage.getItem(CACHE_KEYS.PROJECTS)
      if (cached) {
        return JSON.parse(cached)
      }
    } catch (e) {
      console.warn('Error reading cached projects:', e)
    }
    return null
  },
  
  _cacheProjects(projects: Array<Project> | Array<any>) {
    try {
      if (Array.isArray(projects)) {
        localStorage.setItem(CACHE_KEYS.PROJECTS, JSON.stringify(projects))
        console.debug('Projects cached successfully:', projects.length)
      }
    } catch (e) {
      console.warn('Error caching projects:', e)
    }
  },

  // ========================================
  // Project Management Functions (Dashboard)
  // ========================================
  
  /**
   * Get all projects for the current user
   * Used by dashboard for project listing
   * Tries multiple API paths to find the correct endpoint
   */
  async getProjects() {
    // Check auth token before making requests
    const authHeader = api.defaults.headers.common['Authorization']
    if (!authHeader) {
      console.error('No Authorization header set for project fetch')
      
      // Try to get projects from local cache as fallback
      const cachedProjects = this._getCachedProjects()
      if (cachedProjects) {
        console.debug('Using cached projects due to missing auth header:', cachedProjects.length)
        return cachedProjects
      }
      
      throw new Error('You must be logged in to view projects')
    }
    
    // Try to get projects from local cache while waiting for API
    const cachedProjects = this._getCachedProjects()
    if (cachedProjects) {
      console.debug('Using cached projects while fetching from API:', cachedProjects.length)
      // We'll still try the API, but return the cached data immediately
      setTimeout(() => this._refreshProjectsInBackground(authHeader), 100)
      return cachedProjects
    }
    
    // Update the order of API paths to try the project_manager endpoint first
    const apiPaths = [
      API_PATHS.PROJECT_MANAGER + '/projects/',        // Try this first - Django backend uses project_manager
      API_PATHS.PRODUCTS_OASIS_PROJECT_MANAGER + '/projects/',
      API_PATHS.BUILDER + '/projects/',                // Then try builder paths
      API_PATHS.PRODUCTS_OASIS_BUILDER + '/projects/',
      API_PATHS.CORE_BUILDER + '/projects/',
      API_PATHS.DIRECT_BUILDER + '/projects/',
      'project-manager/projects/',                     // Try without the API path prefix
      'builder/projects/',
    ]
    
    let lastError: any = null
    
    // Log API configuration details and auth state
    console.debug('Project API - getProjects starting:', {
      baseURL: axios.defaults.baseURL,
      paths: apiPaths,
      authHeaderPresent: !!axios.defaults.headers.common['Authorization'],
      withCredentials: axios.defaults.withCredentials
    })
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        const cleanPath = buildApiUrl(path);
        console.debug(`Making API request to get projects from path: ${cleanPath}`)
        
        // Log the headers being sent for debugging
        console.debug('Auth header present:', !!authHeader)
        
        const response = await api.get(cleanPath)
        
        console.debug(`Project API - getProjects response from ${path}:`, {
          status: response.status,
          statusText: response.statusText,
          data: response.data,
          headers: response.headers,
          dataType: typeof response.data
        })
        
        // Handle both array response and paginated response
        if (Array.isArray(response.data)) {
          console.debug('Response is an array with length:', response.data.length)
          return response.data
        } else if (response.data?.results && Array.isArray(response.data.results)) {
          console.debug('Response has results array with length:', response.data.results.length)
          return response.data.results
        } else if (response.data?.projects && Array.isArray(response.data.projects)) {
          console.debug('Response has projects array with length:', response.data.projects.length)
          return response.data.projects
        } else {
          console.warn(`Unexpected response format from ${path}:`, response.data)
          // Try to extract any array from the response as a fallback
          const possibleArrays = Object.values(response.data || {}).filter(val => Array.isArray(val))
          if (possibleArrays.length > 0) {
            console.debug('Found a possible array in response:', possibleArrays[0])
            return possibleArrays[0]
          }
        }
      } catch (error: any) {
        lastError = error
        console.warn(`API request failed for path ${path}:`, {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        
        // If it's a 401/403 error, no need to try other paths
        if (error.response?.status === 401 || error.response?.status === 403) {
          console.error('Authentication error when fetching projects')
          throw new Error('You must be logged in to view projects')
        }
      }
    }
    
    // Try direct axios call as last resort
    try {
      console.debug('Making direct axios call to /api/v1/builder/projects/')
      const response = await axios.get('/api/v1/builder/projects/', {
        headers: {
          'Authorization': authHeader
        }
      })
      
      console.debug('Direct axios call response:', {
        status: response.status,
        data: response.data
      })
      
      if (Array.isArray(response.data)) {
        return response.data
      } else if (response.data?.results && Array.isArray(response.data.results)) {
        return response.data.results
      }
    } catch (directError: any) {
      console.error('Direct axios call failed:', directError)
    }
    
    // If we've tried all paths and none worked, throw the last error
    if (lastError) {
      if (lastError.response?.status === 403) {
        throw new Error('You do not have permission to view projects.')
      } else if (lastError.response?.data?.detail) {
        throw new Error(`API Error: ${lastError.response.data.detail}`)
      }
      
      throw lastError
    }
    
    // If we got here, all paths failed but we didn't have a specific error
    console.warn('All API paths failed without specific errors - returning empty array')
    return []
  },

  /**
   * Background refresh of projects to update cache
   * Does not throw errors - just updates cache if successful
   */
  async _refreshProjectsInBackground(authHeader: unknown) {
    try {
      const response = await axios.get('/api/v1/project-manager/projects/', {
        headers: {
          'Authorization': String(authHeader)
        }
      })
      
      let projects = null
      
      if (Array.isArray(response.data)) {
        projects = response.data
      } else if (response.data?.results && Array.isArray(response.data.results)) {
        projects = response.data.results
      } else if (response.data?.projects && Array.isArray(response.data.projects)) {
        projects = response.data.projects
      }
      
      if (projects) {
        this._cacheProjects(projects)
        console.debug('Projects refreshed in background:', projects.length)
      }
    } catch (error) {
      console.debug('Background refresh of projects failed:', error)
      // No error handling needed - this is a background refresh
    }
  },

  /**
   * Create a new project
   * Used by dashboard for project creation
   */
  async createProject({ name, description }: { name: string; description: string }): Promise<Project> {
    console.debug('Project API - creating project:', { name, description })
    
    try {
      const response = await api.post(buildApiUrl(`${API_PATHS.CORE_BUILDER}/projects/`), {
        name,
        description
      })
      
      console.debug('Project API - createProject response:', {
        status: response.status,
        data: response.data
      })
      
      // Check if we got a valid project response
      if (!response.data || !response.data.id) {
        throw new Error('Invalid project data received from server')
      }
      
      return response.data
    } catch (error: any) {
      console.error('Project API - createProject error:', error)
      
      if (error.response?.status === 400 && error.response?.data?.name) {
        throw new Error(`Name error: ${error.response.data.name}`)
      } else if (error.response?.status === 400 && error.response?.data?.description) {
        throw new Error(`Description error: ${error.response.data.description}`)
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to create a project')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to create projects')
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      }
      
      throw error
    }
  },

  /**
   * Update a project's details
   * Used by dashboard for project editing (not file content)
   */
  async updateProject(projectId: string, data: Partial<Project>): Promise<Project> {
    console.debug('Project API - updating project:', { projectId, data })
    
    try {
      const response = await api.patch(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/`,
        data
      )
      
      console.debug('Project API - updateProject response:', {
        status: response.status,
        data: response.data
      })
      
      return response.data
    } catch (error: any) {
      console.error('Project API - updateProject error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to update a project')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to update this project')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      }
      
      throw error
    }
  },

  /**
   * Delete a project
   * Used by dashboard for project deletion
   */
  async deleteProject(projectId: string): Promise<void> {
    console.debug('Project API - deleting project:', { projectId })
    
    try {
      const response = await api.delete(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/`
      )
      
      console.debug('Project API - deleteProject response:', {
        status: response.status
      })
    } catch (error: any) {
      console.error('Project API - deleteProject error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found or already deleted')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to delete a project')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to delete this project')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      }
      
      throw error
    }
  },

  /**
   * Get details for a specific project
   * Used by workspace to load project data
   */
  async getProject(projectId: string, fullData = false): Promise<Project> {
    console.debug('Project API - getting project:', { projectId, fullData })
    
    try {
      const url = buildApiUrl(`${API_PATHS.CORE_BUILDER}/projects/${projectId}/`)
      const response = await api.get(url, {
        params: fullData ? { full_data: true } : {}
      })
      
      console.debug('Project API - getProject response:', {
        status: response.status,
        dataSize: JSON.stringify(response.data).length
      })
      
      return response.data
    } catch (error: any) {
      console.error('Project API - getProject error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to view this project')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to view this project')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      }
      
      throw error
    }
  },

  /**
   * Get dashboard activities
   * Used by dashboard only
   */
  async getActivities(): Promise<Activity[]> {
    try {
      const response = await api.get(`${API_PATHS.CORE_BUILDER}/activities/`)
      return response.data?.results || []
    } catch (error) {
      console.error('Failed to fetch activities:', error)
      return []
    }
  },

  /**
   * Get dashboard stats
   * Used by dashboard only
   */
  async getStats(): Promise<DashboardStats> {
    try {
      const response = await api.get(`${API_PATHS.CORE_BUILDER}/stats/`)
      return response.data || { 
        activeBuildCount: 0, 
        apiCallCount: 0, 
        creditsUsed: 0,
        projectCount: 0,
        creditsRemaining: 0,
        totalBuilds: 0,
        successRate: 0,
        lastUpdateTime: new Date().toISOString()
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error)
      return { 
        activeBuildCount: 0, 
        apiCallCount: 0, 
        creditsUsed: 0,
        projectCount: 0,
        creditsRemaining: 0,
        totalBuilds: 0,
        successRate: 0,
        lastUpdateTime: new Date().toISOString()
      }
    }
  },

  // ========================================
  // Project Files Functions (Workspace)
  // ========================================
  
  /**
   * Get all files for a project
   * Used by workspace for file listing
   */
  async getProjectFiles(projectId: string): Promise<ProjectFile[]> {
    console.debug('Project API - getting project files:', { projectId })
    
    try {
      const response = await api.get(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/files/`
      )
      
      console.debug('Project API - getProjectFiles response:', {
        status: response.status,
        fileCount: response.data?.length
      })
      
      return response.data || []
    } catch (error: any) {
      console.error('Project API - getProjectFiles error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to view project files')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to view files for this project')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      }
      
      throw error
    }
  },

  /**
   * Get a specific file by path
   * Used by workspace for file editing
   */
  async getFile(projectId: string, filePath: string): Promise<ProjectFile> {
    console.debug('Project API - getting file:', { projectId, filePath })
    
    try {
      const response = await api.get(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/files/${encodeURIComponent(filePath)}/`
      )
      
      console.debug('Project API - getFile response:', {
        status: response.status,
        contentLength: response.data?.content?.length
      })
      
      return response.data
    } catch (error: any) {
      console.error('Project API - getFile error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('File not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to view this file')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to view this file')
      }
      
      throw error
    }
  },

  /**
   * Create a new file
   * Used by workspace for file creation
   * Will ensure parent directories exist by creating them if needed
   */
  async createFile(
    projectId: string,
    filePath: string,
    content: string
  ): Promise<ProjectFile> {
    console.debug('Project API - creating file:', { projectId, filePath, contentLength: content.length })
    
    // Check if we need to create parent directories first
    const pathParts = filePath.split('/')
    if (pathParts.length > 1) {
      // Remove the file name to get the directory path
      pathParts.pop()
      const directoryPath = pathParts.join('/')
      
      if (directoryPath) {
        console.debug('Project API - ensuring directory exists:', { projectId, directoryPath })
        try {
          // Try to create the directory structure first
          await this.createDirectory(projectId, directoryPath)
        } catch (error: any) {
          // Ignore 409 errors (directory already exists)
          if (error.response?.status !== 409) {
            console.error('Project API - failed to create parent directory:', error)
            throw error
          }
        }
      }
    }
    
    // Now create the actual file
    try {
      const response = await api.post(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/files/`,
        {
          path: filePath,
          content
        }
      )
      
      console.debug('Project API - createFile response:', {
        status: response.status,
        data: response.data
      })
      
      return response.data
    } catch (error: any) {
      console.error('Project API - createFile error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found')
      } else if (error.response?.status === 409) {
        throw new Error('File already exists')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to create files')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to create files in this project')
      }
      
      throw error
    }
  },

  /**
   * Create a directory
   * Used by workspace for directory creation
   */
  async createDirectory(projectId: string, directoryPath: string): Promise<void> {
    console.debug('Project API - creating directory:', { projectId, directoryPath })
    
    try {
      const response = await api.post(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/directories/`,
        {
          path: directoryPath
        }
      )
      
      console.debug('Project API - createDirectory response:', {
        status: response.status
      })
    } catch (error: any) {
      console.error('Project API - createDirectory error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found')
      } else if (error.response?.status === 409) {
        // Directory already exists, which is fine
        console.debug('Directory already exists:', directoryPath)
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to create directories')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to create directories in this project')
      } else {
        throw error
      }
    }
  },

  /**
   * Update file content
   * Used by workspace for file editing
   */
  async updateFileContent(
    projectId: string,
    filePath: string,
    content: string
  ): Promise<ProjectFile> {
    console.debug('Project API - updating file content:', { 
      projectId, 
      filePath, 
      contentLength: content.length 
    })
    
    try {
      const response = await api.put(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/files/${encodeURIComponent(filePath)}/`,
        {
          content
        }
      )
      
      console.debug('Project API - updateFileContent response:', {
        status: response.status,
        data: response.data
      })
      
      return response.data
    } catch (error: any) {
      console.error('Project API - updateFileContent error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('File not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to update files')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to update this file')
      }
      
      throw error
    }
  },

  /**
   * Delete a file
   * Used by workspace for file deletion
   */
  async deleteFile(projectId: string, filePath: string): Promise<void> {
    console.debug('Project API - deleting file:', { projectId, filePath })
    
    try {
      const response = await api.delete(
        `${API_PATHS.CORE_BUILDER}/projects/${projectId}/files/${encodeURIComponent(filePath)}/`
      )
      
      console.debug('Project API - deleteFile response:', {
        status: response.status
      })
    } catch (error: any) {
      console.error('Project API - deleteFile error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('File not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to delete files')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to delete this file')
      }
      
      throw error
    }
  }
}

/**
 * Helper function to safely construct API URLs
 * Prevents duplicate /api/v1/ prefixes
 */
function buildApiUrl(path: string) {
  // Strip any leading /api/v1/ to prevent duplication
  const cleanPath = path.replace(/^\/?(api\/v1\/)?/, '');
  return cleanPath;
}