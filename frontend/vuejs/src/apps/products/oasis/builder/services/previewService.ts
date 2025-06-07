import api from './api'
import { buildApiUrl } from '@/shared/services/api'

/**
 * Service for handling preview functionality
 */
export const PreviewService = {
  /**
   * Generate a preview for a project
   * 
   * @param projectId - The ID of the project to preview
   * @returns Promise with the preview URL
   */
  async generatePreview(projectId: string): Promise<{ previewUrl: string }> {
    try {
      const response = await api.get(buildApiUrl(`/api/v1/builder/${projectId}/preview/`));
      return {
        previewUrl: response.data.preview_url
      };
    } catch (error) {
      throw new Error(`Failed to generate preview: ${this.formatError(error)}`);
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
  }
} 