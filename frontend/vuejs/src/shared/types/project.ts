export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  status: 'active' | 'archived' | 'draft';
}

export interface ProjectCreateData {
  name: string;
  description?: string;
}

export function normalizeProject(data: any): Project {
  return {
    id: String(data.id),
    name: data.name,
    description: data.description,
    created_at: data.created_at || data.createdAt || '',
    updated_at: data.updated_at || data.updatedAt || '',
    status: data.status || 'active'
  }
}
