// Types used in Vue components
import type { EditorLanguage } from '@/shared/types/editor'
import { v4 as uuidv4 } from 'uuid'

/**
 * Project file type
 */
export interface ProjectFile {
  id?: string;
  name?: string;
  path: string;
  type: EditorLanguage;
  content?: string;
  lastModified?: string;
  size?: number;
  isDirectory?: boolean;
  children?: ProjectFile[];
}

/**
 * Type for Project display in list items and cards
 */
export interface Project {
  id: string | number;
  name: string;
  description?: string;
  created_at: string;
  updated_at?: string;
  version?: string;
  is_active?: boolean;
  user_id?: number;
  files?: any[];
  is_initialized?: boolean;
  project_path?: string;
  generation_status?: string;
}

/**
 * Properties for ProjectList component
 */
export interface ProjectListProps {
  projects: Project[];
  isLoading: boolean;
  error: string;
}

/**
 * Normalize a project object from the API
 * This ensures consistent structure regardless of API response format
 */
export function normalizeProject(data: any): Project {
  if (!data) return {} as Project

  // Ensure ID is always a string to avoid type issues with routing
  const id = data.id ? String(data.id) : uuidv4()

  return {
    id: id,
    name: (data.name || 'Untitled Project').trim(),
    description: (data.description || '').trim(),
    created_at: data.created_at || data.createdAt || new Date().toISOString(),
    updated_at: data.updated_at || data.updatedAt || new Date().toISOString(),
    is_active: data.is_active !== undefined ? data.is_active : true,
    user_id: data.user_id || data.user || undefined,
    files: data.files || [],
    is_initialized: data.is_initialized !== undefined ? data.is_initialized : false,
    project_path: data.project_path || '',
    generation_status: data.generation_status || 'pending'
  }
} 