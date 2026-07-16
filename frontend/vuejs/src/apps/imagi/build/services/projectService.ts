import api from '@/shared/services/api'
import type { Project } from '../types/components'

// Define cache keys
const CACHE_KEYS = {
  PROJECTS: 'imagi_cached_projects',
  PROJECT_PREFIX: 'imagi_project_'
}

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
   * Fetch a project's status, including the generation_status that tracks
   * the initial AI build ('pending' | 'generating' | 'completed' | 'failed')
   */
  async getProjectStatus(projectId: string): Promise<{
    id: number
    name: string
    is_initialized: boolean
    generation_status: 'pending' | 'generating' | 'completed' | 'failed'
  }> {
    const response = await api.get(`/v1/project-manager/projects/${projectId}/status/`)
    return response.data
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
  }
}

