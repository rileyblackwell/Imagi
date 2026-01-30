import api from '@/shared/services/api'
import type { Project, ProjectFile } from '../types/components'
import { useAuthStore } from '@/shared/stores/auth'
import { FileService } from './fileService'


// Define API path constants
const API_PATHS = {
  PROJECT_MANAGER: '/v1/project-manager',
  BUILDER: '/v1/builder',
  AGENTS: '/v1/agents'
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
   * Uses the correct Django API endpoint
   */
  async getProjects(force = false) {
    // Check auth token before making requests
    const authHeader = api.defaults.headers.common['Authorization']
    
    console.debug('Project API - getProjects starting:', {
      baseURL: api.defaults.baseURL,
      authHeaderPresent: !!authHeader,
      windowLocation: window.location.origin
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
    
    // Only use cache if not forcing a fresh fetch
    if (!force) {
      const cachedProjects = this._getCachedProjects()
      if (cachedProjects) {
        // Return cached data immediately - don't run background refresh
        // This prevents interference with explicit refresh operations
        console.debug('Returning cached projects without background refresh')
        return cachedProjects
      }
    }
    
    // Use the correct Django API endpoint based on URL patterns
    const endpoint = '/v1/project-manager/projects/'
    
    try {
      console.debug(`Making API request to get projects from path: ${endpoint}`)
      console.debug('Full request config:', {
        url: endpoint,
        baseURL: api.defaults.baseURL,
        authHeader: !!api.defaults.headers.common['Authorization'],
        timeout: api.defaults.timeout
      })
      
      const response = await api.get(endpoint)
      
      console.debug(`Project API - getProjects response:`, {
        status: response.status,
        statusText: response.statusText,
        dataType: typeof response.data,
        url: response.config?.url
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
        console.warn(`Unexpected response format from ${endpoint}:`, response.data)
        // Try to extract any array from the response as a fallback
        const possibleArrays = Object.values(response.data || {}).filter(val => Array.isArray(val))
        if (possibleArrays.length > 0) {
          console.debug('Found a possible array in response:', possibleArrays[0])
          this._cacheProjects(possibleArrays[0] as any[]) // Cache the successful response
          return possibleArrays[0]
        }
      }
    } catch (error: any) {
      console.error(`API request failed for path ${endpoint}:`, {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config,
        message: error.message
      })
      
      // If it's a 401/403 error, handle authentication
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.error('Authentication error when fetching projects')
        throw new Error('You must be logged in to view projects')
      }
      
      // Re-throw the error for the calling code to handle
      throw error
    }
    
    // If we reach here, something went wrong
    throw new Error('Failed to fetch projects - no data received')
  },

  /**
   * Background refresh of projects to update cache
   * Does not throw errors - just updates cache if successful
   */
  async _refreshProjectsInBackground(authHeader: unknown) {
    try {
      const response = await api.get('/v1/project-manager/projects/', {
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
      // API endpoint for creating projects
      const response = await api.post('/v1/project-manager/projects/create/', {
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
      
      // Clear cache after project creation to ensure fresh data on next fetch
      this._clearProjectsCache()
      console.debug('Projects cache cleared after creation')
      
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
   * Initialize a project by setting up required files and configurations
   * 
   * @param projectId - The ID of the project to initialize
   * @returns Promise with success status
   */
  async initializeProject(projectId: string): Promise<{ success: boolean }> {
    try {
      await api.post(`/v1/project-manager/projects/${projectId}/initialize/`);
      return { success: true };
    } catch (error) {
      throw new Error(`Failed to initialize project: ${this.formatError(error)}`);
    }
  },

  /**
   * Format an error object or string into a readable message
   * 
   * @param error - The error to format
   * @returns Formatted error message
   */
  formatError(error: any): string {
    if (error instanceof Error) {
      return error.message;
    } else if (typeof error === 'string') {
      return error;
    } else if (error && error.response && error.response.data) {
      const data = error.response.data;
      
      if (data.detail) {
        return data.detail;
      } else if (data.message) {
        return data.message;
      } else if (data.error) {
        return data.error;
      } else if (typeof data === 'string') {
        return data;
      } else {
        try {
          return JSON.stringify(data);
        } catch (e) {
          return 'Unknown error occurred';
        }
      }
    } else if (error && error.message) {
      return error.message;
    } else {
      try {
        return JSON.stringify(error);
      } catch (e) {
        return 'Unknown error occurred';
      }
    }
  },

  /**
   * Update an existing project
   * Used by dashboard for project editing (not file content)
   */
  async updateProject(projectId: string, data: Partial<Project>): Promise<Project> {
    console.debug('Project API - updating project:', { projectId, data })
    
    try {
      // Use ProjectManager API directly
      const updateUrl = `/v1/project-manager/projects/${projectId}/`
      console.debug('Project API - updateProject URL:', updateUrl)
      
      const response = await api.patch(updateUrl, data)
      
      console.debug('Project API - updateProject response:', {
        status: response.status,
        data: response.data
      })
      
      // Clear cache after project update to ensure fresh data on next fetch
      this._clearProjectsCache()
      console.debug('Projects cache cleared after update')
      
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
      // Ensure proper URL construction for proxying
      const deleteUrl = `/v1/project-manager/projects/${projectId}/delete/`
      console.debug('Project API - deleteProject URL:', deleteUrl)
      
      const response = await api.delete(deleteUrl)
      
      console.debug('Project API - deleteProject response:', {
        status: response.status
      })
      
      // Clear cache immediately after successful deletion to prevent showing stale data
      this._clearProjectsCache()
      console.debug('Project cache cleared after deletion')
      
    } catch (error: any) {
      console.error('Project API - deleteProject error:', error)
      
      if (error.response?.status === 404) {
        // Project was already deleted, clear cache anyway
        this._clearProjectsCache()
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
   * Clear the projects cache
   * Used when projects need to be refreshed from server
   */
  _clearProjectsCache() {
    try {
      localStorage.removeItem(CACHE_KEYS.PROJECTS)
      console.debug('Projects cache cleared')
    } catch (e) {
      console.warn('Error clearing projects cache:', e)
    }
  },

  /**
   * Public method to clear projects cache
   * Used by store when immediate cache invalidation is needed
   */
  clearProjectsCache() {
    this._clearProjectsCache()
  },

  /**
   * Get details for a specific project
   * Used by workspace to load project data
   */
  async getProject(projectId: string, fullData = false): Promise<Project> {
    console.debug('Project API - getting project:', { projectId, fullData })
    
    // Ensure projectId is a string
    const projectIdStr = String(projectId);
    
    // Use the primary Django API endpoint for project details
    const endpoint = `/v1/project-manager/projects/${projectIdStr}/`
    
    try {
      console.debug(`Making API request to get project from path: ${endpoint}`)
      console.debug('Full request config:', {
        url: endpoint,
        baseURL: api.defaults.baseURL,
        authHeader: !!api.defaults.headers.common['Authorization'],
        params: fullData ? { full_data: true } : {}
      })
      
      const response = await api.get(endpoint, {
        params: fullData ? { full_data: true } : {}
      })

      // Check if response is HTML instead of JSON
      const contentType = response.headers['content-type'] || '';
      if (contentType.includes('text/html') || 
          (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE'))) {
        console.error('Received HTML response instead of JSON:', {
          url: endpoint,
          contentType,
          dataStart: typeof response.data === 'string' ? response.data.substring(0, 50) : 'not a string'
        });
        throw new Error('Invalid response format: received HTML instead of JSON');
      }
      
      console.debug(`Project API - getProject response:`, {
        status: response.status,
        dataSize: JSON.stringify(response.data).length,
        url: response.config?.url
      })
      
      return response.data
    } catch (error: any) {
      console.error(`API request failed for project detail path ${endpoint}:`, {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: error.config,
        message: error.message
      })
      
      // Handle specific error cases
      if (error.response?.status === 401) {
        throw new Error('You must be logged in to view this project')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to view this project')
      } else if (error.response?.status === 404) {
        throw new Error('Project not found')
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

  /**
   * Test API connection by trying multiple endpoints
   * Used for diagnostics when there are connection issues
   */
  async testApiConnection(): Promise<{ success: boolean; endpoint?: string; projects?: any[] }> {
    try {
      // Get token
      const tokenData = localStorage.getItem('token')
      if (!tokenData) {
        return { success: false }
      }
      
      const parsedToken = JSON.parse(tokenData)
      if (!parsedToken || !parsedToken.value) {
        return { success: false }
      }
      
      const token = parsedToken.value
      
      // Try different API endpoints - use only standardized endpoints
      const endpoints = [
        'api/v1/project-manager/projects/',  // Primary endpoint
        'api/v1/builder/builder/',          // Fallback endpoint
        'api/v1/agents/projects/'            // Another possible endpoint
      ]
      
      for (const endpoint of endpoints) {
        try {
          const response = await api.get(endpoint, {
            headers: {
              'Authorization': `Token ${token}`
            }
          })
          
          if (Array.isArray(response.data) || response.data?.results) {
            const projectData = Array.isArray(response.data) ? response.data : response.data.results
            console.debug(`Successfully fetched ${projectData.length} projects from ${endpoint}`)
            return { 
              success: true, 
              endpoint, 
              projects: projectData 
            }
          }
        } catch (error) {
          console.debug(`API test failed for endpoint ${endpoint}:`, error)
        }
      }
      
      return { success: false }
    } catch (error) {
      console.debug('API test failed:', error)
      return { success: false }
    }
  },

  /**
   * Run comprehensive diagnostics for project loading issues
   * Returns diagnostic information and attempts to resolve issues
   */
  async runDiagnostics(): Promise<{ success: boolean; details: any }> {
    console.debug('Running project loading diagnostics...')
    
    const diagnostics = {
      authToken: null as string | null,
      apiHeadersSet: false,
      connectionTest: null as any,
      errors: [] as string[]
    }
    
    try {
      // Check authentication state
      const authStore = useAuthStore() as any
      
      diagnostics.authToken = authStore.token ? 'exists' : 'missing'
      diagnostics.apiHeadersSet = !!api.defaults.headers.common['Authorization']
      
      console.debug('Auth diagnostics:', {
        authStoreAuthenticated: authStore.isAuthenticated,
        token: diagnostics.authToken,
        apiHeadersSet: diagnostics.apiHeadersSet
      })
      
      // Ensure token is set in API headers
      if (authStore.token && !diagnostics.apiHeadersSet) {
        api.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
        diagnostics.apiHeadersSet = true
        console.debug('Set Authorization header for diagnostics')
      }
      
      // Try direct access to API
      diagnostics.connectionTest = await this.testApiConnection()
      
      return {
        success: diagnostics.connectionTest.success,
        details: diagnostics
      }
    } catch (error: any) {
      diagnostics.errors.push(error.message || 'Unknown error during diagnostics')
      return {
        success: false,
        details: diagnostics
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
    await (FileService as any).createDirectory(projectId, directoryPath)
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
    
    // Redirect to FileService (returns boolean, but we return void for backward compatibility)
    await (FileService as any).deleteFile(projectId, filePath)
    return
  }
}

