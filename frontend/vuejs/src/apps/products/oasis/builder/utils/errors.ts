import axios, { AxiosError } from 'axios'

// Error handling utilities
export class BuilderAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any,
    public isProjectNotFound: boolean = false
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
    const isNotFound = statusCode === 404

    // Return early if no status code is available
    if (!statusCode) {
      return new BuilderAPIError(
        details?.message || axiosError.message || 'Network error occurred',
        undefined,
        details,
        false
      )
    }

    if (statusCode === 401) {
      return new BuilderAPIError('Session expired. Please log in again.', statusCode, details, false)
    }
    
    if (statusCode === 403) {
      return new BuilderAPIError('You do not have permission to perform this action.', statusCode, details, false)
    }

    if (statusCode === 404) {
      return new BuilderAPIError('The requested resource was not found.', statusCode, details, true)
    }

    if (statusCode === 429) {
      return new BuilderAPIError('API rate limit exceeded. Please try again later.', statusCode, details, false)
    }

    if (statusCode >= 500) {
      return new BuilderAPIError('Server error. Please try again later.', statusCode, details, false)
    }

    return new BuilderAPIError(
      details?.message || axiosError.message || 'An unknown error occurred',
      statusCode,
      details,
      false
    )
  }

  if (error instanceof Error) {
    return new BuilderAPIError(error.message, undefined, undefined, false)
  }

  return new BuilderAPIError('An unknown error occurred', undefined, undefined, false)
}