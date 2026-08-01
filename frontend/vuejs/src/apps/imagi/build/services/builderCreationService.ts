import api from '@/shared/services/api'

/**
 * Service for handling app, view, and component creation via backend APIs
 */
export class BuilderCreationService {
  /**
   * Ensure default apps exist (home, auth)
   */
  static async ensureDefaultApps(
    projectId: string
  ): Promise<{ 
    success: boolean; 
    message?: string; 
    error?: string;
    created_apps?: string[];
    existing_frontend?: boolean;
  }> {
    try {
      const response = await api.post(`/v1/builder/${projectId}/apps/create/`, {
        action: 'ensure_defaults'
      })
      
      return response.data
    } catch (error: any) {
      console.error('Error ensuring default apps:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to ensure default apps'
      }
    }
  }
}
