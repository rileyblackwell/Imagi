import axios, { AxiosError } from 'axios'

// Error handling utilities
export class BuilderAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any
  ) {
    super(message)
    this.name = 'BuilderAPIError'
  }
}

export function handleAPIError(error: unknown): BuilderAPIError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>
    const statusCode = axiosError.response?.status
    const details = axiosError.response?.data

    // Return early if no status code is available
    if (!statusCode) {
      return new BuilderAPIError(
        details?.message || axiosError.message || 'Network error occurred',
        undefined,
        details
      )
    }

    if (statusCode === 401) {
      return new BuilderAPIError('Session expired. Please log in again.', statusCode, details)
    }
    
    if (statusCode === 403) {
      return new BuilderAPIError('You do not have permission to perform this action.', statusCode, details)
    }

    if (statusCode === 404) {
      return new BuilderAPIError('The requested resource was not found.', statusCode, details)
    }

    if (statusCode === 429) {
      return new BuilderAPIError('API rate limit exceeded. Please try again later.', statusCode, details)
    }

    if (statusCode >= 500) {
      return new BuilderAPIError('Server error. Please try again later.', statusCode, details)
    }

    return new BuilderAPIError(
      details?.message || axiosError.message || 'An unknown error occurred',
      statusCode,
      details
    )
  }

  if (error instanceof Error) {
    return new BuilderAPIError(error.message)
  }

  return new BuilderAPIError('An unknown error occurred')
}