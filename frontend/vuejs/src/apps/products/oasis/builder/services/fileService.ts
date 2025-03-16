import api from './api'
import type { ProjectFile } from '../types/builder'

// Define API path constants
const API_PATHS = {
  BUILDER: 'api/v1/builder'
}

/**
 * File Service
 * 
 * This service handles communication with the backend API for file operations:
 * - Listing project files
 * - Getting file content
 * - Creating files
 * - Updating files
 * - Deleting files
 */
export const FileService = {
  /**
   * Get all files for a project
   * Used by workspace for file listing
   */
  async getProjectFiles(projectId: string): Promise<ProjectFile[]> {
    console.debug('File API - getting project files:', { projectId })
    
    // Builder API paths for file operations
    const apiPaths = [
      // Main builder API path (should be primary path)
      `/api/v1/builder/builder/${projectId}/files/`,
      
      // Alternative paths as fallbacks
      `${API_PATHS.BUILDER}/builder/${projectId}/files/`,
    ]
    
    let lastError: any = null;
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        console.debug(`Making API request to get project files from path: ${path}`)
        
        const response = await api.get(path)
        
        console.debug(`File API - getProjectFiles response from ${path}:`, {
          status: response.status,
          fileCount: response.data?.length
        })
        
        return response.data || []
      } catch (error: any) {
        lastError = error
        console.warn(`API request failed for project files path ${path}:`, {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        
        // If it's a 401/403 error, no need to try other paths
        if (error.response?.status === 401 || error.response?.status === 403) {
          if (error.response?.status === 401) {
            throw new Error('You must be logged in to view project files')
          } else {
            throw new Error('You do not have permission to view files for this project')
          }
        }
      }
    }
    
    // If we've tried all paths and none worked, throw the last error
    if (lastError) {
      console.error('File API - getProjectFiles error:', lastError)
      
      if (lastError.response?.status === 404) {
        throw new Error('Project files not found. The project may not be initialized yet.')
      } else if (lastError.response?.data?.detail) {
        throw new Error(lastError.response.data.detail)
      }
      
      throw lastError
    }
    
    throw new Error('Failed to fetch project files')
  },

  /**
   * Get a specific file by path
   * Used by workspace for file editing
   */
  async getFile(projectId: string, filePath: string): Promise<ProjectFile> {
    console.debug('File API - getting file:', { projectId, filePath })
    
    // Builder API paths for file operations
    const apiPaths = [
      // Main builder API path (should be primary path)
      `/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/`,
      
      // Content-specific endpoint as a fallback
      `/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/content/`,
      
      // Alternative paths as fallbacks
      `${API_PATHS.BUILDER}/builder/${projectId}/files/${encodeURIComponent(filePath)}/`,
    ]
    
    let lastError: any = null;
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        console.debug(`Making API request to get file from path: ${path}`)
        
        const response = await api.get(path)
        
        console.debug(`File API - getFile response from ${path}:`, {
          status: response.status,
          contentLength: response.data?.content?.length
        })
        
        return response.data
      } catch (error: any) {
        lastError = error
        console.warn(`API request failed for get file path ${path}:`, {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        
        // If it's a 401/403 error, no need to try other paths
        if (error.response?.status === 401 || error.response?.status === 403) {
          if (error.response?.status === 401) {
            throw new Error('You must be logged in to view this file')
          } else {
            throw new Error('You do not have permission to view this file')
          }
        }
      }
    }
    
    // If we've tried all paths and none worked, throw the last error
    if (lastError) {
      console.error('File API - getFile error:', lastError)
      
      if (lastError.response?.status === 404) {
        throw new Error('File not found. The project may not be initialized yet.')
      } else if (lastError.response?.status === 401) {
        throw new Error('You must be logged in to view this file')
      } else if (lastError.response?.status === 403) {
        throw new Error('You do not have permission to view this file')
      } else if (lastError.response?.data?.detail) {
        throw new Error(lastError.response.data.detail)
      }
      
      throw lastError
    }
    
    throw new Error('Failed to fetch file')
  },

  /**
   * Create a new file
   * Used by workspace for file creation
   */
  async createFile(
    projectId: string,
    filePath: string,
    content: string
  ): Promise<ProjectFile> {
    console.debug('File API - creating file:', { projectId, filePath })
    
    // Builder API paths for file operations
    const apiPaths = [
      // Main builder API path (should be primary path)
      `/api/v1/builder/builder/${projectId}/files/`,
      
      // Alternative paths as fallbacks
      `${API_PATHS.BUILDER}/builder/${projectId}/files/`,
    ]
    
    let lastError: any = null;
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        console.debug(`Making API request to create file using path: ${path}`)
        
        const response = await api.post(path, {
          path: filePath,
          content
        })
        
        console.debug(`File API - createFile response from ${path}:`, {
          status: response.status,
          data: response.data
        })
        
        return response.data
      } catch (error: any) {
        lastError = error
        console.warn(`API request failed for create file path ${path}:`, {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        
        // If it's a 401/403 error, no need to try other paths
        if (error.response?.status === 401 || error.response?.status === 403) {
          if (error.response?.status === 401) {
            throw new Error('You must be logged in to create files')
          } else {
            throw new Error('You do not have permission to create files in this project')
          }
        }
      }
    }
    
    // If we've tried all paths and none worked, throw the last error
    if (lastError) {
      console.error('File API - createFile error:', lastError)
      
      if (lastError.response?.status === 404) {
        throw new Error('Project not found or not initialized')
      } else if (lastError.response?.status === 409) {
        throw new Error('File already exists')
      } else if (lastError.response?.data?.detail) {
        throw new Error(lastError.response.data.detail)
      }
      
      throw lastError
    }
    
    throw new Error('Failed to create file')
  },

  /**
   * Create a directory
   * Used by workspace for directory creation
   */
  async createDirectory(projectId: string, directoryPath: string): Promise<void> {
    console.debug('File API - creating directory:', { projectId, directoryPath })
    
    try {
      const response = await api.post(
        `/api/v1/builder/builder/${projectId}/directories/`,
        {
          path: directoryPath
        }
      )
      
      console.debug('File API - createDirectory response:', {
        status: response.status
      })
    } catch (error: any) {
      console.error('File API - createDirectory error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found or not initialized')
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
    console.debug('File API - updating file:', { projectId, filePath })
    
    // Builder API paths for file operations
    const apiPaths = [
      // Main builder API path (should be primary path)
      `/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/`,
      
      // Alternative paths as fallbacks
      `${API_PATHS.BUILDER}/builder/${projectId}/files/${encodeURIComponent(filePath)}/`,
    ]
    
    let lastError: any = null;
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        console.debug(`Making API request to update file using path: ${path}`)
        
        const response = await api.put(path, {
          content
        })
        
        console.debug(`File API - updateFileContent response:`, {
          status: response.status,
          data: response.data
        })
        
        return response.data
      } catch (error: any) {
        lastError = error
        console.warn(`API request failed for update file path ${path}:`, {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        
        // If it's a 401/403 error, no need to try other paths
        if (error.response?.status === 401 || error.response?.status === 403) {
          if (error.response?.status === 401) {
            throw new Error('You must be logged in to update files')
          } else {
            throw new Error('You do not have permission to update files in this project')
          }
        }
      }
    }
    
    // If we've tried all paths and none worked, throw the last error
    if (lastError) {
      console.error('File API - updateFileContent error:', lastError)
      
      if (lastError.response?.status === 404) {
        throw new Error('File not found or project not initialized')
      } else if (lastError.response?.data?.detail) {
        throw new Error(lastError.response.data.detail)
      }
      
      throw lastError
    }
    
    throw new Error('Failed to update file')
  },

  /**
   * Delete a file
   * Used by workspace for file deletion
   */
  async deleteFile(projectId: string, filePath: string): Promise<void> {
    console.debug('File API - deleting file:', { projectId, filePath })
    
    // Builder API paths for file operations
    const apiPaths = [
      // Main builder API path (should be primary path)
      `/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/`,
      
      // Alternative paths as fallbacks
      `${API_PATHS.BUILDER}/builder/${projectId}/files/${encodeURIComponent(filePath)}/`,
    ]
    
    let lastError: any = null;
    
    // Try each path in sequence
    for (const path of apiPaths) {
      try {
        console.debug(`Making API request to delete file using path: ${path}`)
        
        const response = await api.delete(path)
        
        console.debug(`File API - deleteFile response:`, {
          status: response.status
        })
        
        return
      } catch (error: any) {
        lastError = error
        console.warn(`API request failed for delete file path ${path}:`, {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data
        })
        
        // If it's a 401/403 error, no need to try other paths
        if (error.response?.status === 401 || error.response?.status === 403) {
          if (error.response?.status === 401) {
            throw new Error('You must be logged in to delete files')
          } else {
            throw new Error('You do not have permission to delete files in this project')
          }
        }
      }
    }
    
    // If we've tried all paths and none worked, throw the last error
    if (lastError) {
      console.error('File API - deleteFile error:', lastError)
      
      if (lastError.response?.status === 404) {
        // File already deleted or never existed - consider this a success
        return
      } else if (lastError.response?.data?.detail) {
        throw new Error(lastError.response.data.detail)
      }
      
      throw lastError
    }
  }
}

export default FileService 