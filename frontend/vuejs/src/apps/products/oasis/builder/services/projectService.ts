import axios from 'axios'
import api from './api'
import { handleAPIError } from '../utils/errors'
import type { Project, ProjectFile } from '../types/components'
import { normalizeProject } from '../types/components'

// Define API path constants
const API_PATHS = {
  PROJECT_MANAGER: 'api/v1/project-manager',
  BUILDER: 'api/v1/builder',
  AGENTS: 'api/v1/agents'
}

// Define cache keys
const CACHE_KEYS = {
  PROJECTS: 'imagi_cached_projects',
  PROJECT_PREFIX: 'imagi_project_'
}

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
    
    console.debug('Project API - getProjects starting:', {
      baseURL: api.defaults.baseURL,
      authHeaderPresent: !!authHeader
    })
    
    if (!authHeader) {
      // Try to get token from localStorage as the API headers might not be set yet
      try {
        const tokenData = localStorage.getItem('token')
        if (tokenData) {
          const parsedToken = JSON.parse(tokenData)
          if (parsedToken && parsedToken.value) {
            // Set the token in the API headers
            api.defaults.headers.common['Authorization'] = `Token ${parsedToken.value}`
            console.debug('Set Authorization header from localStorage')
          }
        }
      } catch (e) {
        console.warn('Error reading token from localStorage:', e)
      }
      
      // If still no auth header after attempting to set it
      if (!api.defaults.headers.common['Authorization']) {
        // Try to get projects from local cache as fallback
        const cachedProjects = this._getCachedProjects()
        if (cachedProjects) {
          return cachedProjects
        }
        
        throw new Error('You must be logged in to view projects')
      }
    }
    
    // Try to get projects from local cache while waiting for API
    const cachedProjects = this._getCachedProjects()
    if (cachedProjects) {
      // We'll still try the API, but return the cached data immediately
      setTimeout(() => this._refreshProjectsInBackground(api.defaults.headers.common['Authorization']), 100)
      return cachedProjects
    }
    
    // Update the order of API paths to try the project_manager endpoint first
    const apiPaths = [
      'api/v1/project-manager/projects/',  // Primary endpoint matching Django backend URLs
      API_PATHS.PROJECT_MANAGER + '/projects/',
      'api/v1/builder/builder/',          // Fallback endpoint using new URL structure
      API_PATHS.BUILDER + '/builder/',
    ]
    
    let lastError: any = null
    
    // Log API configuration details and auth state
    console.debug('Project API - getProjects paths to try:', apiPaths)
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        const cleanPath = path.startsWith('/') ? path.substring(1) : path;
        console.debug(`Making API request to get projects from path: ${cleanPath}`)
        
        // Debug log auth header to verify it's being sent
        console.debug('Auth header present in request:', !!api.defaults.headers.common['Authorization'])
        
        const response = await api.get(cleanPath)
        
        console.debug(`Project API - getProjects response from ${path}:`, {
          status: response.status,
          statusText: response.statusText,
          dataType: typeof response.data
        })
        
        // Handle both array response and paginated response
        if (Array.isArray(response.data)) {
          console.debug('Response is an array with length:', response.data.length)
          this._cacheProjects(response.data) // Cache the successful response
          return response.data
        } else if (response.data?.results && Array.isArray(response.data.results)) {
          console.debug('Response has results array with length:', response.data.results.length)
          this._cacheProjects(response.data.results) // Cache the successful response
          return response.data.results
        } else if (response.data?.projects && Array.isArray(response.data.projects)) {
          console.debug('Response has projects array with length:', response.data.projects.length)
          this._cacheProjects(response.data.projects) // Cache the successful response
          return response.data.projects
        } else {
          console.warn(`Unexpected response format from ${path}:`, response.data)
          // Try to extract any array from the response as a fallback
          const possibleArrays = Object.values(response.data || {}).filter(val => Array.isArray(val))
          if (possibleArrays.length > 0) {
            console.debug('Found a possible array in response:', possibleArrays[0])
            this._cacheProjects(possibleArrays[0] as any[]) // Cache the successful response
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
          // Try one more time with a direct approach
          try {
            // Attempt to refresh the token from localStorage
            const tokenData = localStorage.getItem('token')
            if (tokenData) {
              const parsedToken = JSON.parse(tokenData)
              if (parsedToken && parsedToken.value) {
                // Update the token in the API headers
                api.defaults.headers.common['Authorization'] = `Token ${parsedToken.value}`
                // Try again with the first path only
                const retryResponse = await api.get(apiPaths[0])
                if (Array.isArray(retryResponse.data)) {
                  return retryResponse.data
                } else if (retryResponse.data?.results && Array.isArray(retryResponse.data.results)) {
                  return retryResponse.data.results
                }
              }
            }
          } catch (retryError) {
            console.error('Retry with refreshed token failed:', retryError)
          }
          
          throw new Error('You must be logged in to view projects')
        }
      }
    }
    
    // Try direct axios call as last resort
    try {
      console.debug('Making direct axios call to /api/v1/project-manager/projects/')
      const response = await axios.get('/api/v1/project-manager/projects/', {
        headers: {
          'Authorization': String(api.defaults.headers.common['Authorization'])
        }
      })
      
      console.debug('Direct axios call response:', {
        status: response.status,
        data: response.data
      })
      
      if (Array.isArray(response.data)) {
        this._cacheProjects(response.data)
        return response.data
      } else if (response.data?.results && Array.isArray(response.data.results)) {
        this._cacheProjects(response.data.results)
        return response.data.results
      }
    } catch (directError: any) {
      console.error('Direct axios call failed:', directError)
    }
    
    // If we got here after trying everything, check if we have cached projects as a last resort
    const lastResortCache = this._getCachedProjects()
    if (lastResortCache && Array.isArray(lastResortCache) && lastResortCache.length > 0) {
      console.debug('Using cached projects as last resort after API failures')
      return lastResortCache
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
      // Update to match the exact URL structure in backend/django/apps/Products/Oasis/ProjectManager/api/urls.py
      const response = await api.post(`api/v1/project-manager/projects/create/`, {
        name,
        description
      })
      
      console.debug('Project API - createProject response:', {
        status: response.status,
        data: response.data,
        responseType: typeof response.data,
        id: response.data?.id,
        idType: typeof response.data?.id
      })
      
      // Check if we got a valid project response
      if (!response.data || !response.data.id) {
        throw new Error('Invalid project data received from server')
      }
      
      // Ensure the ID is a string to avoid type issues with routing
      if (response.data.id) {
        response.data.id = String(response.data.id);
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
   * Initialize a project after creation
   * This sets up the initial project structure
   */
  async initializeProject(projectId: string): Promise<any> {
    console.debug('Project API - initializing project:', { projectId })
    
    if (!projectId) {
      console.error('Project API - initializeProject: No project ID provided')
      throw new Error('Project ID is required')
    }
    
    try {
      // First, check if the project is already initialized
      const statusResponse = await api.get(
        `api/v1/project-manager/projects/${projectId}/status/`
      )
      
      console.debug('Project API - project status check:', {
        status: statusResponse.status,
        data: statusResponse.data
      })
      
      // If project is already initialized, return immediately
      if (statusResponse.data?.is_initialized) {
        console.debug('Project is already initialized, skipping initialization')
        return {
          success: true,
          already_initialized: true,
          is_initialized: true,
          project_id: statusResponse.data.id,
          name: statusResponse.data.name
        }
      }
      
      // Add a small delay to ensure any previous operations are completed
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Otherwise, proceed with initialization
      console.debug('Project not initialized, sending initialization request')
      
      // Use a timeout to prevent hanging requests
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30 second timeout
      
      try {
        const response = await api.post(
          `api/v1/project-manager/projects/${projectId}/initialize/`,
          {}, // empty body
          { signal: controller.signal }
        )
        
        clearTimeout(timeoutId)
        
        console.debug('Project API - initializeProject response:', {
          status: response.status,
          data: response.data
        })
        
        return response.data
      } catch (initError: any) {
        clearTimeout(timeoutId)
        throw initError
      }
    } catch (error: any) {
      console.error('Project API - initializeProject error:', error)
      
      // If it's an abort error, provide a clearer message
      if (error.name === 'AbortError' || error.message?.includes('aborted')) {
        throw new Error('Project initialization timed out. The server might be busy, please try again later.')
      }
      
      if (error.response?.status === 404) {
        throw new Error('Project not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to initialize a project')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to initialize this project')
      } else if (error.response?.status === 409) {
        // Project already initialized is not an error
        console.debug('Project already initialized')
        return { 
          success: true, 
          already_initialized: true,
          project_id: projectId
        }
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else if (error.response?.data?.error) {
        throw new Error(error.response.data.error)
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
        `${API_PATHS.BUILDER}/projects/${projectId}/`,
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
      // Update to match the exact URL structure in backend/django/apps/Products/Oasis/ProjectManager/api/urls.py
      const response = await api.delete(
        `api/v1/project-manager/projects/${projectId}/delete/`
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
    
    // Ensure projectId is a string
    const projectIdStr = String(projectId);
    
    // Try multiple API paths, starting with project-manager
    const apiPaths = [
      // Try direct paths first with explicit API endpoint
      'api/v1/project-manager/projects/' + projectIdStr + '/',
      'api/v1/project-manager/projects/detail/' + projectIdStr + '/',
      'api/v1/builder/builder/' + projectIdStr + '/',
      
      // Then try the standard paths
      API_PATHS.PROJECT_MANAGER + '/projects/' + projectIdStr + '/',
      API_PATHS.BUILDER + '/projects/' + projectIdStr + '/',
    ]
    
    let lastError: any = null;
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        const cleanPath = buildApiUrl(path);
        console.debug(`Making API request to get project from path: ${cleanPath}`)
        
        const response = await api.get(cleanPath, {
          params: fullData ? { full_data: true } : {}
        })

        // Check if response is HTML instead of JSON
        const contentType = response.headers['content-type'] || '';
        if (contentType.includes('text/html') || 
            (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE'))) {
          console.error('Received HTML response instead of JSON:', {
            url: cleanPath,
            contentType,
            dataStart: typeof response.data === 'string' ? response.data.substring(0, 50) : 'not a string'
          });
          throw new Error('Invalid response format: received HTML instead of JSON');
        }
        
        console.debug(`Project API - getProject response from ${cleanPath}:`, {
          status: response.status,
          dataSize: JSON.stringify(response.data).length
        })
        
        return response.data
      } catch (error: any) {
        lastError = error
        console.warn(`API request failed for project detail path ${path}:`, {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
          message: error.message
        })
        
        // If it's a 401/403 error, no need to try other paths
        if (error.response?.status === 401 || error.response?.status === 403) {
          if (error.response?.status === 401) {
            throw new Error('You must be logged in to view this project')
          } else {
            throw new Error('You do not have permission to view this project')
          }
        }
      }
    }
    
    // Try direct axios call as last resort with both endpoints
    for (const baseEndpoint of ['project-manager', 'builder']) {
      try {
        const absolutePath = `/api/v1/${baseEndpoint}/projects/${projectIdStr}/`
        console.debug(`Making direct axios call to ${absolutePath}`)
        
        const response = await axios.get(absolutePath, {
          headers: api.defaults.headers.common,
          params: fullData ? { full_data: true } : {},
          // Set validateStatus to prevent axios from rejecting non-2xx responses
          validateStatus: (status) => status < 500
        })
        
        // Log the content type and check if response is HTML
        const contentType = response.headers['content-type'] || '';
        console.debug('Direct axios call response:', {
          status: response.status,
          contentType,
          dataType: typeof response.data,
          dataStart: typeof response.data === 'string' ? response.data.substring(0, 50) : 'not a string'
        })

        // Check if response is HTML instead of JSON
        if (contentType.includes('text/html') || 
            (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE'))) {
          console.error('Received HTML response instead of JSON');
          continue; // Skip this endpoint and try the next one
        }
        
        if (response.status >= 200 && response.status < 300) {
          return response.data;
        }
      } catch (directError: any) {
        console.error(`Direct axios call to ${baseEndpoint} failed:`, directError)
      }
    }
    
    // If we've tried all paths and none worked, throw the last error
    if (lastError) {
      console.error('Project API - getProject error:', lastError)
      
      if (lastError.response?.status === 404) {
        throw new Error('Project not found')
      } else if (lastError.response?.data?.detail) {
        throw new Error(lastError.response.data.detail)
      }
      
      throw lastError
    }
    
    throw new Error('Failed to fetch project data')
  },

  /**
   * Get dashboard activities
   * Used by dashboard only
   */
  async getActivities(): Promise<Activity[]> {
    try {
      const response = await api.get(`${API_PATHS.BUILDER}/activities/`)
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
      const response = await api.get(`${API_PATHS.BUILDER}/stats/`)
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
    
    // DEPRECATED: This method is now moved to FileService.
    // This is kept for backward compatibility but will log a warning.
    console.warn('ProjectService.getProjectFiles is deprecated. Please use FileService.getProjectFiles instead.')
    
    // Redirect to FileService
    const { FileService } = await import('./fileService')
    return FileService.getProjectFiles(projectId) as unknown as ProjectFile[]
  },

  /**
   * Get a specific file by path
   * Used by workspace for file editing
   */
  async getFile(projectId: string, filePath: string): Promise<ProjectFile> {
    console.debug('Project API - getting file:', { projectId, filePath })
    
    // DEPRECATED: This method is now moved to FileService.
    // This is kept for backward compatibility but will log a warning.
    console.warn('ProjectService.getFile is deprecated. Please use FileService.getFile instead.')
    
    // Redirect to FileService
    const { FileService } = await import('./fileService')
    return FileService.getFile(projectId, filePath) as unknown as ProjectFile
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
    console.debug('Project API - creating file:', { projectId, filePath })
    
    // DEPRECATED: This method is now moved to FileService.
    // This is kept for backward compatibility but will log a warning.
    console.warn('ProjectService.createFile is deprecated. Please use FileService.createFile instead.')
    
    // Redirect to FileService
    const { FileService } = await import('./fileService')
    return FileService.createFile(projectId, filePath, content) as unknown as ProjectFile
  },

  /**
   * Create a directory
   * Used by workspace for directory creation
   */
  async createDirectory(projectId: string, directoryPath: string): Promise<void> {
    console.debug('Project API - creating directory:', { projectId, directoryPath })
    
    // DEPRECATED: This method is now moved to FileService.
    // This is kept for backward compatibility but will log a warning.
    console.warn('ProjectService.createDirectory is deprecated. Please use FileService.createDirectory instead.')
    
    // Redirect to FileService
    const { FileService } = await import('./fileService')
    return FileService.createDirectory(projectId, directoryPath)
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
    console.debug('Project API - updating file content:', { projectId, filePath })
    
    // DEPRECATED: This method is now moved to FileService.
    // This is kept for backward compatibility but will log a warning.
    console.warn('ProjectService.updateFileContent is deprecated. Please use FileService.updateFileContent instead.')
    
    // Redirect to FileService
    const { FileService } = await import('./fileService')
    return FileService.updateFileContent(projectId, filePath, content) as unknown as ProjectFile
  },

  /**
   * Delete a file
   * Used by workspace for file deletion
   */
  async deleteFile(projectId: string, filePath: string): Promise<void> {
    console.debug('Project API - deleting file:', { projectId, filePath })
    
    // DEPRECATED: This method is now moved to FileService.
    // This is kept for backward compatibility but will log a warning.
    console.warn('ProjectService.deleteFile is deprecated. Please use FileService.deleteFile instead.')
    
    // Redirect to FileService
    const { FileService } = await import('./fileService')
    await FileService.deleteFile(projectId, filePath)
    // No return value needed since this method returns void
  }
}

/**
 * Helper function to build a proper API URL
 */
function buildApiUrl(path: string) {
  // Remove leading slashes for consistency
  const cleanPath = path.startsWith('/') ? path.substring(1) : path;
  
  // If already has api/v1/ prefix, use as is, otherwise add it
  return cleanPath.startsWith('api/v1/') ? cleanPath : `api/v1/${cleanPath}`;
}