import api from './api'
import type { ProjectFile, EditorLanguage } from '../types/index'

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
   * Get all files in a project
   */
  async getProjectFiles(projectId: string): Promise<ProjectFile[]> {
    console.debug('File API - getting project files:', { projectId })
    
    try {
      // Try to get all files from the consolidated API endpoint first (backward compatibility)
      try {
        const response = await api.get(`/api/v1/builder/builder/${projectId}/directories/`)
        
        // Check if response is HTML instead of JSON
        const contentType = response.headers['content-type'] || '';
        if (contentType.includes('text/html') || 
            (typeof response.data === 'string' && response.data.trim().startsWith('<!DOCTYPE'))) {
          console.error('Received HTML response instead of JSON:', {
            contentType,
            dataStart: typeof response.data === 'string' ? response.data.substring(0, 50) : 'not a string'
          });
          throw new Error('Invalid response format: received HTML instead of JSON');
        }
        
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          console.debug('File API - retrieved files using directories endpoint:', response.data.length)
          return response.data || []
        }
      } catch (dirError) {
        console.warn('File API - directories endpoint failed, trying separate endpoints:', dirError)
      }
      
      // If the directories endpoint failed or returned empty, try the new separate endpoints
      console.debug('File API - trying separate template and static endpoints')
      
      // Get project details to check if the project exists and is accessible
      const detailsResponse = await api.get(`/api/v1/builder/builder/${projectId}/details/`)
      
      // Check if details response is HTML
      const detailsContentType = detailsResponse.headers['content-type'] || '';
      if (detailsContentType.includes('text/html') || 
          (typeof detailsResponse.data === 'string' && detailsResponse.data.trim().startsWith('<!DOCTYPE'))) {
        console.error('Received HTML response for details endpoint:', {
          contentType: detailsContentType,
          dataStart: typeof detailsResponse.data === 'string' ? detailsResponse.data.substring(0, 50) : 'not a string'
        });
        throw new Error('Invalid response format: received HTML instead of JSON');
      }
      
      if (!detailsResponse.data) {
        throw new Error('Project not found or not initialized')
      }
      
      // Get templates
      const templatesResponse = await api.get(`/api/v1/builder/builder/${projectId}/templates/`)
      const templateFiles = templatesResponse.data || []
      
      // Get static files
      const staticResponse = await api.get(`/api/v1/builder/builder/${projectId}/static/`)
      const staticFiles = staticResponse.data || []
      
      // Combine the results
      const allFiles = [...templateFiles, ...staticFiles]
      console.debug('File API - retrieved files using separate endpoints:', allFiles.length)
      
      return allFiles
    } catch (error: any) {
      console.error('File API - getProjectFiles error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('Project not found or not initialized')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to access project files')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to access this project')
      }
      
      throw error
    }
  },
  
  /**
   * Get files from a specific directory
   */
  async getDirectoryFiles(projectId: string, directory: string): Promise<ProjectFile[]> {
    console.debug('File API - getting directory files:', { projectId, directory })
    
    try {
      // Get all files from the API
      const response = await api.get(`/api/v1/builder/builder/${projectId}/directories/`)
      const allFiles = response.data || []
      
      // Filter files by directory
      return allFiles.filter((file: ProjectFile) => file.path.startsWith(directory))
    } catch (error: any) {
      console.error('File API - getDirectoryFiles error:', error)
      throw error
    }
  },

  /**
   * Get a file by path
   */
  async getFile(projectId: string, filePath: string): Promise<ProjectFile> {
    console.debug('File API - getting file:', { projectId, filePath })
    
    try {
      // Get the file content using the content endpoint
      const content = await this.getFileContent(projectId, filePath)
      
      // Determine file type from extension
      const fileExtension = filePath.split('.').pop() || ''
      const fileName = filePath.split('/').pop() || ''
      let fileType: EditorLanguage = 'html'
      
      if (fileExtension === 'html') {
        fileType = 'html'
      } else if (fileExtension === 'css') {
        fileType = 'css'
      } else if (fileExtension === 'js' || fileExtension === 'javascript') {
        fileType = 'javascript'
      } else if (fileExtension === 'ts' || fileExtension === 'typescript') {
        fileType = 'typescript'
      } else if (fileExtension === 'py') {
        fileType = 'python'
      } else if (fileExtension === 'vue') {
        fileType = 'vue'
      }
      
      // Return file details
      return {
        id: `${projectId}-${filePath}`,
        name: fileName,
        path: filePath,
        type: fileType,
        content: content,
        lastModified: new Date().toISOString()
      }
    } catch (error: any) {
      console.error('File API - getFile error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('File not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to access this file')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to access this file')
      }
      
      throw error
    }
  },

  /**
   * Get file content
   */
  async getFileContent(projectId: string, filePath: string): Promise<string> {
    console.debug('File API - getting file content:', { projectId, filePath })
    
    try {
      const response = await api.get(`/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/content/`)
      return response.data.content || ''
    } catch (error: any) {
      console.error('File API - getFileContent error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('File not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to access this file')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to access this file')
      }
      
      throw error
    }
  },

  /**
   * Update file content
   */
  async updateFileContent(projectId: string, filePath: string, content: string): Promise<ProjectFile> {
    console.debug('File API - updating file content:', { projectId, filePath })
    
    try {
      // First, check if the file exists by trying to get its content
      try {
        await this.getFileContent(projectId, filePath)
      } catch (error) {
        // If the file doesn't exist, create it
        return this.createFile(projectId, filePath, content)
      }
      
      // Create a temporary file with the new content
      const tempFilePath = `${filePath}.new`
      await this.createFile(projectId, tempFilePath, content)
      
      // Delete the original file
      await this.deleteFile(projectId, filePath)
      
      // Rename the temporary file to the original name
      const newFile = await this.createFile(projectId, filePath, content)
      
      // Delete the temporary file
      try {
        await this.deleteFile(projectId, tempFilePath)
      } catch (error) {
        // Ignore errors here
        console.warn(`Could not delete temporary file ${tempFilePath}`)
      }
      
      return newFile
    } catch (error: any) {
      console.error('File API - updateFileContent error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('File not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to update this file')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to update this file')
      }
      
      throw error
    }
  },

  /**
   * Create a new file
   */
  async createFile(projectId: string, filePath: string, content: string = ''): Promise<ProjectFile> {
    console.debug('File API - creating file:', { projectId, filePath })
    
    try {
      const response = await api.post(`/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/content/`, {
        content
      })
      
      console.debug('File API - createFile response:', {
        status: response.status,
        data: response.data
      })
      
      // Generate file details from path
      const fileExtension = filePath.split('.').pop() || ''
      const fileName = filePath.split('/').pop() || ''
      let fileType: EditorLanguage = 'html'
      
      if (fileExtension === 'html') {
        fileType = 'html'
      } else if (fileExtension === 'css') {
        fileType = 'css'
      } else if (fileExtension === 'js' || fileExtension === 'javascript') {
        fileType = 'javascript'
      } else if (fileExtension === 'ts' || fileExtension === 'typescript') {
        fileType = 'typescript'
      } else if (fileExtension === 'py') {
        fileType = 'python'
      } else if (fileExtension === 'vue') {
        fileType = 'vue'
      }
      
      return {
        id: `${projectId}-${filePath}`,
        name: fileName,
        path: filePath,
        type: fileType,
        content: content,
        lastModified: new Date().toISOString()
      }
    } catch (error: any) {
      console.error('File API - createFile error:', error)
      
      if (error.response?.status === 409) {
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
   * Delete a file
   */
  async deleteFile(projectId: string, filePath: string): Promise<boolean> {
    console.debug('File API - deleting file:', { projectId, filePath })
    
    try {
      await api.delete(`/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/content/`)
      return true
    } catch (error: any) {
      console.error('File API - deleteFile error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('File not found')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to delete files')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to delete files in this project')
      }
      
      throw error
    }
  },

  /**
   * Undo the last change to a specific file
   */
  async undoFileChanges(projectId: string, filePath: string): Promise<string> {
    console.debug('File API - undoing file changes:', { projectId, filePath })
    
    try {
      const response = await api.post(`/api/v1/builder/builder/${projectId}/files/${encodeURIComponent(filePath)}/undo/`)
      
      console.debug('File API - undoFileChanges response:', {
        status: response.status,
        data: response.data
      })
      
      if (response.data && response.data.content) {
        return response.data.content
      }
      
      return ''
    } catch (error: any) {
      console.error('File API - undoFileChanges error:', error)
      
      if (error.response?.status === 404) {
        throw new Error('No previous version found for this file')
      } else if (error.response?.status === 401) {
        throw new Error('You must be logged in to undo changes')
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to undo changes in this project')
      }
      
      throw error
    }
  }
}

export default FileService
