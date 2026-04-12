/**
 * Layout Service
 * Handles saving and loading project layout positions and connections
 */

import api from '@/shared/services/api'

export interface LayoutPosition {
  x: number
  y: number
}

export interface LayoutConnection {
  from: string
  to: string
}

export interface LayoutData {
  positions: Record<string, LayoutPosition>
  connections: LayoutConnection[]
}

export interface LayoutResponse {
  success: boolean
  layout_data?: LayoutData
  updated_at?: string
  message?: string
  error?: string
}

export class LayoutService {
  /**
   * Load saved layout for a project
   */
  static async loadLayout(projectId: string): Promise<LayoutResponse> {
    try {
      const response = await api.get(`/api/v1/builder/${projectId}/layout/`)
      return response.data
    } catch (error: any) {
      console.error('Error loading layout:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to load layout',
        layout_data: { positions: {}, connections: [] }
      }
    }
  }

  /**
   * Save layout positions and connections
   */
  static async saveLayout(projectId: string, layoutData: LayoutData): Promise<LayoutResponse> {
    try {
      const response = await api.post(`/api/v1/builder/${projectId}/layout/`, {
        layout_data: layoutData
      })
      return response.data
    } catch (error: any) {
      console.error('Error saving layout:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to save layout'
      }
    }
  }

  /**
   * Reset layout to default (delete saved layout)
   */
  static async resetLayout(projectId: string): Promise<LayoutResponse> {
    try {
      const response = await api.delete(`/api/v1/builder/${projectId}/layout/`)
      return response.data
    } catch (error: any) {
      console.error('Error resetting layout:', error)
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to reset layout'
      }
    }
  }
}

