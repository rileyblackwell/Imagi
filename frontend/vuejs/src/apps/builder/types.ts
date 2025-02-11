export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  status: ProjectStatus;
}

export type ProjectStatus = 'active' | 'draft' | 'archived';

export interface ProjectListItemProps {
  project: Project;
}

export interface StatusClasses {
  [key: string]: string;
  active: string;
  draft: string;
  archived: string;
}
