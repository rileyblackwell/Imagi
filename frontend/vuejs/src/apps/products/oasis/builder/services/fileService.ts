import api from './api'
import type { ProjectFile, EditorLanguage } from '../types/index'

// Define API path constants
const API_PATHS = {
  BUILDER: 'api/v1/builder'
}

/**
 * Safely encode URI components while handling invalid URI characters
 * This function wraps encodeURIComponent with additional error handling
 */
function safeEncodeURIComponent(component: string): string {
  try {
    // First replace any potentially problematic characters
    const safeComponent = component
      .replace(/%/g, '_pct_')  // Replace % with _pct_
      .replace(/\\/g, '/');    // Replace backslashes with forward slashes
      
    return encodeURIComponent(safeComponent);
  } catch (error) {
    console.error('Error encoding URI component:', error);
    // Fall back to a simplified encoding that just handles spaces and basic special chars
    return component
      .replace(/%/g, '_pct_')
      .replace(/\\/g, '/')
      .replace(/\s+/g, '_')
      .replace(/[&=?#+]/g, '_');
  }
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
        const response = await api.get(`/api/v1/builder/${projectId}/directories/`)
        
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
      
      const detailsResponse = await api.get(`/api/v1/builder/${projectId}/details/`)
      
      if (detailsResponse.data && detailsResponse.data.file_counts) {
        console.log('File API - project details retrieved:', detailsResponse.data)
      }
      
      // Get templates first
      const templatesResponse = await api.get(`/api/v1/builder/${projectId}/templates/`)
      const templates = templatesResponse.data || []
      
      // Then get static files
      const staticResponse = await api.get(`/api/v1/builder/${projectId}/static/`)
      const staticFiles = staticResponse.data || []
      
      // Combine results
      const combinedFiles = [...templates, ...staticFiles]
      
      console.debug('File API - retrieved files using separate endpoints:', combinedFiles.length)
      return combinedFiles
    } catch (error) {
      console.error('File API - error getting project files:', error)
      throw error
    }
  },
  
  /**
   * Get files in a specific directory
   */
  async getDirectoryFiles(projectId: string, directory: string): Promise<ProjectFile[]> {
    console.debug('File API - getting directory files:', { projectId, directory })
    
    try {
      const response = await api.get(`/api/v1/builder/${projectId}/directories/`)
      
      if (!response.data || !Array.isArray(response.data)) {
        return []
      }
      
      // Filter files by directory
      return response.data.filter(file => {
        // Check if the file is in the requested directory
        // This handles both files directly in the directory and in subdirectories
        return file.path.startsWith(directory)
      })
    } catch (error) {
      console.error('File API - error getting directory files:', error)
      throw error
    }
  },
  
  /**
   * Get a specific file by path
   */
  async getFile(projectId: string, filePath: string): Promise<ProjectFile> {
    console.debug('File API - getting file:', { projectId, filePath })
    
    try {
      // Get all files and find the one we want
      const files = await this.getProjectFiles(projectId)
      const file = files.find(f => f.path === filePath)
      
      if (!file) {
        throw new Error(`File not found: ${filePath}`)
      }
      
      return file
    } catch (error) {
      console.error('File API - error getting file:', error)
      throw error
    }
  },
  
  /**
   * Get file content by path
   */
  async getFileContent(projectId: string, filePath: string): Promise<string> {
    console.debug('File API - getting file content:', { projectId, filePath })
    
    try {
      const response = await api.get(`/api/v1/builder/${projectId}/files/${safeEncodeURIComponent(filePath)}/content/`)
      
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
      
      return response.data?.content || ''
    } catch (error) {
      console.error('File API - error getting file content:', error)
      throw error
    }
  },
  
  /**
   * Update file content
   */
  async updateFileContent(projectId: string, filePath: string, content: string): Promise<ProjectFile> {
    const fileExtension = filePath.split('.').pop()?.toLowerCase() || '';
    const isCSS = fileExtension === 'css';
    
    // Log with appropriate level of detail
    if (isCSS) {
      console.info('FileService - updating CSS file content:', { 
        projectId, 
        filePath, 
        contentLength: content.length,
        contentPreview: content.substring(0, 50) + '...'
      });
    } else {
      console.debug('File API - updating file content:', { 
        projectId, 
        filePath, 
        contentLength: content.length 
      });
    }
    
    try {
      // Check if the file exists
      try {
        await this.getFile(projectId, filePath)
      } catch (fileError) {
        console.warn('File not found, creating it instead:', fileError)
        return this.createFile(projectId, filePath, content)
      }
      
      // For CSS files, ensure the static/css directory exists
      if (isCSS && filePath.includes('static/css/')) {
        try {
          // Try to ensure the directory exists
          const dirPath = filePath.substring(0, filePath.lastIndexOf('/'));
          await this.createDirectory(projectId, dirPath).catch(err => {
            // Ignore errors if directory already exists
            console.debug('Directory may already exist:', err);
          });
        } catch (dirError) {
          console.debug('Error ensuring directory exists (may be ok):', dirError);
        }
      }
      
      // Include a timestamp in the API call for cache-busting
      const timestamp = Date.now();
      const api_url = `/api/v1/builder/${projectId}/files/${safeEncodeURIComponent(filePath)}/content/?_t=${timestamp}`;
      
      // Log the API call for CSS files
      if (isCSS) {
        console.info(`Sending CSS update to endpoint: ${api_url}`);
      }
      
      const response = await api.post(api_url, {
        content
      });
      
      // Log success for CSS files
      if (isCSS) {
        console.info(`Successfully updated CSS file: ${filePath}`, { 
          status: response.status,
          responseType: typeof response.data
        });
      }
      
      return response.data
    } catch (error: any) {
      // Enhanced error logging for CSS files
      if (isCSS) {
        console.error('Error updating CSS file content:', { 
          projectId, 
          filePath, 
          error: error.message, 
          status: error.response?.status,
          responseData: error.response?.data
        });
      } else {
        console.error('File API - error updating file content:', error);
      }
      
      // Provide more details in the error message
      const errorMsg = error.response?.data?.detail || error.message || 'Unknown error';
      throw new Error(`Failed to update file ${filePath}: ${errorMsg}`);
    }
  },
  
  /**
   * Create a new file
   */
  async createFile(projectId: string, filePath: string, content: string = ''): Promise<ProjectFile> {
    console.debug('File API - creating file:', { projectId, filePath, contentLength: content.length })
    
    try {
      const response = await api.post(`/api/v1/builder/${projectId}/files/create/`, {
        path: filePath,
        content
      })
      
      return response.data
    } catch (error) {
      console.error('File API - error creating file:', error)
      throw error
    }
  },

  /**
   * Create a new directory
   */
  async createDirectory(projectId: string, directoryPath: string): Promise<void> {
    console.debug('File API - creating directory:', { projectId, directoryPath })
    
    try {
      // Ensure the directory path ends with a /
      const normalizedPath = directoryPath.endsWith('/') ? directoryPath : `${directoryPath}/`
      
      // Create a placeholder file in the directory
      const placeholderPath = `${normalizedPath}.gitkeep`
      
      await api.post(`/api/v1/builder/${projectId}/directories/`, {
        path: normalizedPath
      })
      
      console.debug('Directory created successfully')
    } catch (error) {
      console.error('File API - error creating directory:', error)
      throw error
    }
  },

  /**
   * Delete a file
   */
  async deleteFile(projectId: string, filePath: string): Promise<boolean> {
    console.debug('File API - deleting file:', { projectId, filePath })
    
    try {
      // Try DELETE method first (REST standard)
      try {
        await api.delete(`/api/v1/builder/${projectId}/files/${safeEncodeURIComponent(filePath)}/delete/`)
      } catch (deleteError) {
        console.warn('DELETE method failed, trying POST method:', deleteError)
        await api.post(`/api/v1/builder/${projectId}/files/${safeEncodeURIComponent(filePath)}/delete/`)
      }
      
      return true
    } catch (error) {
      console.error('File API - error deleting file:', error)
      throw error
    }
  },
  
  /**
   * Undo file changes
   */
  async undoFileChanges(projectId: string, filePath: string): Promise<string> {
    console.debug('File API - undoing file changes:', { projectId, filePath })
    
    try {
      const response = await api.post(`/api/v1/builder/${projectId}/files/${safeEncodeURIComponent(filePath)}/undo/`)
      
      return response.data?.content || ''
    } catch (error) {
      console.error('File API - error undoing file changes:', error)
      throw error
    }
  }
}

export default FileService
