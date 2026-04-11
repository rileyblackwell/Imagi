import api from '@/shared/services/api'

interface HealthCheckResponse {
  status: string
  service: string
  database: string
}

export async function checkBackendHealth(): Promise<HealthCheckResponse> {
  const response = await api.get<HealthCheckResponse>('/v1/home/health/')
  return response.data
}
