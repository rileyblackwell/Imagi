import { v4 as uuidv4 } from 'uuid'

export interface Project {
  id: string | number
  name: string
  description: string
  created_at: string
  updated_at: string
  is_active: boolean
  user_id?: number
  files?: any[]
}

export interface ProjectData {
  name: string
  description?: string
}

/**
 * Normalize a project object from the API
 * This ensures consistent structure regardless of API response format
 */
export function normalizeProject(data: any): Project {
  // Handle case where data might be null or undefined
  if (!data) {
    return {
      id: uuidv4(),
      name: 'Unknown Project',
      description: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_active: true,
      files: []
    }
  }

  // Ensure we have an ID (either from API or generate one)
  const id = data.id || uuidv4()
  
  // Create normalized project object
  return {
    id,
    name: data.name || 'Untitled Project',
    description: data.description || '',
    created_at: data.created_at || new Date().toISOString(),
    updated_at: data.updated_at || new Date().toISOString(),
    is_active: data.is_active !== undefined ? data.is_active : true,
    user_id: data.user_id || data.user || undefined,
    files: data.files || []
  }
}
