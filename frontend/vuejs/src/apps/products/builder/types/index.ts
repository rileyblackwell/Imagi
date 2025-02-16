export * from './builder'  // Export everything from builder.ts

export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  status: ProjectStatus;
}

export type ProjectStatus = 'active' | 'draft' | 'archived';

// Remove duplicate ProjectType interface since it's now in builder.ts

export interface ProjectListItemProps {
  project: Project;
}

export interface StatusClasses {
  [key: string]: string;
  active: string;
  draft: string;
  archived: string;
}

export type BuilderMode = 'chat' | 'build';

export interface ProjectFile {
  path: string;
  type: string;
  content?: string;
}
