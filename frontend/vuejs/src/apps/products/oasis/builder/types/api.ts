// Types for API responses
export interface APIErrorResponse {
  error?: string;
  message?: string;
  detail?: string;
}

export interface APIPagination {
  count: number;
  next: string | null;
  previous: string | null;
}

export interface APIListResponse<T> {
  data: T[];
  pagination?: APIPagination;
}

export interface APIDetailResponse<T> {
  data: T;
  message?: string;
}

// AI-specific response types
export interface AIMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  code?: string;
}

export interface AIGenerationResponse {
  code?: string;
  response?: string;
  messages?: AIMessage[];
  success: boolean;
  error?: string;
}