import api, { buildApiUrl } from '@/shared/services/api'

/**
 * Service for handling app, view, and component creation via backend APIs
 */
export class BuilderCreationService {
  /**
   * Create a new Vue.js app from gallery
   */
  static async createAppFromGallery(
    projectId: string, 
    appName: string, 
    appDescription?: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await api.post(buildApiUrl(`/builder/${projectId}/apps/create/`), {
        action: 'create_app',
        app_name: appName,
        app_description: appDescription || ''
      })
      
      return response.data
    } catch (error: any) {
      console.error('Error creating app from gallery:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to create app'
      }
    }
  }

  /**
   * Ensure default apps exist (home, auth, payments)
   */
  static async ensureDefaultApps(
    projectId: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await api.post(buildApiUrl(`/builder/${projectId}/apps/create/`), {
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

  /**
   * Create a new Vue.js view within an app
   */
  static async createView(
    projectId: string,
    appName: string,
    viewName: string,
    pageType: string = 'view',
    routePath?: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const requestData: any = {
        app_name: appName,
        page_name: viewName,
        page_type: pageType
      }
      
      if (routePath) {
        requestData.route_path = routePath
      }
      
      const response = await api.post(buildApiUrl(`/builder/${projectId}/views/create/`), requestData)
      
      return response.data
    } catch (error: any) {
      console.error('Error creating view:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to create view'
      }
    }
  }

  /**
   * Backward-compatible alias for createView
   */
  static async createPage(
    projectId: string,
    appName: string,
    pageName: string,
    pageType: string = 'view',
    routePath?: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    return this.createView(projectId, appName, pageName, pageType, routePath)
  }

  /**
   * Create a new Vue.js atomic component
   */
  static async createComponent(
    projectId: string,
    appName: string,
    componentName: string,
    componentType: string = 'atom',
    componentVariant: string = 'generic'
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await api.post(buildApiUrl(`/builder/${projectId}/components/create/`), {
        app_name: appName,
        component_name: componentName,
        component_type: componentType,
        component_variant: componentVariant
      })
      
      return response.data
    } catch (error: any) {
      console.error('Error creating component:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to create component'
      }
    }
  }

  /**
   * Create a specialized button component
   */
  static async createButtonComponent(
    projectId: string,
    appName: string,
    buttonName: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    return this.createComponent(projectId, appName, buttonName, 'atom', 'button')
  }

  /**
   * Create a specialized input component
   */
  static async createInputComponent(
    projectId: string,
    appName: string,
    inputName: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    return this.createComponent(projectId, appName, inputName, 'atom', 'input')
  }
}
