export type ActivityType = 'created' | 'updated' | 'deleted' | 'deployed'

export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt: string;
  status: 'active' | 'archived' | 'draft';
}

export interface Activity {
  id: string;
  type: ActivityType;
  message: string;
  createdAt: string;
  userId?: string;
  projectId?: string;
  metadata?: Record<string, any>;
}

export interface DashboardStats {
  projectCount: number;
  activeBuildCount: number;
  creditsUsed: number;
  apiCallCount: number;
  creditsRemaining: number;
  totalBuilds: number;
  successRate: number;
  lastUpdateTime: string;
}

export interface DashboardState {
  activities: Activity[];
  stats: DashboardStats | null;
  loading: boolean;
  error: string | null;
}

export interface QuickAction {
  title: string;
  icon: string;
  route: string | { name: string };
}

export interface Resource {
  title: string;
  icon: string;
  url: string;
  description: string;
}
