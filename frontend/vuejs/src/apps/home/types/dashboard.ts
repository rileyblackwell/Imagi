export type ActivityType = 'created' | 'updated' | 'deleted' | 'deployed'

export interface Activity {
  id: string;
  type: ActivityType;
  message: string;
  createdAt: string;
  userId?: string;
  projectId?: string;
  metadata?: Record<string, any>;
}
