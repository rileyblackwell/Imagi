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
      return new BuilderAPIError('The requested resource was not found.', statusCode, details, false)
    }

    if (statusCode === 429) {
      return new BuilderAPIError('API rate limit exceeded. Please try again later.', statusCode, details, false)
    }

    if (statusCode >= 500) {
      // Check if the server returned HTML instead of JSON
      if (typeof details === 'string' && details.includes('<!DOCTYPE html>')) {
        console.error('Server error returned HTML instead of JSON', details.substring(0, 200));
        return new BuilderAPIError(
          'Server error occurred. The API returned an error page instead of proper JSON response.',
          statusCode,
          { htmlResponse: true },
          false
        )
      }
      
      // Try to extract useful information from the server error
      let errorMessage = 'Server error. Please try again later.';
      
      // If there's a detailed error message, use it
      if (details && details.error) {
        errorMessage = `Server error: ${details.error}`;
      } else if (details && details.message) {
        errorMessage = `Server error: ${details.message}`;
      } else if (details && details.detail) {
        errorMessage = `Server error: ${details.detail}`;
      }
      
      // Log the full error details for debugging
      console.error('Server error details:', {
        status: statusCode,
        message: axiosError.message,
        data: details
      });
      
      return new BuilderAPIError(errorMessage, statusCode, details, false)
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