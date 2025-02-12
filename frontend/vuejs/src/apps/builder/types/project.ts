export interface Project {
  id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
  status: 'active' | 'archived' | 'draft'
}

export interface ProjectData {
  name: string
  description?: string
}

export function normalizeProject(data: unknown): Project {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid project data')
  }

  const project = data as any
  return {
    id: String(project.id),
    name: String(project.name || ''),
    description: project.description?.toString(),
    created_at: project.created_at || new Date().toISOString(),
    updated_at: project.updated_at || new Date().toISOString(),
    status: project.status || 'draft'
  }
}
