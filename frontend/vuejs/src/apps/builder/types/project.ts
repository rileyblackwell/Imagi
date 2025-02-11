export interface Project {
  id: number;
  name: string;
  description?: string;
  status: 'draft' | 'published';
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ProjectCreateData {
  name: string;
  description?: string;
}
