import axios, { AxiosError } from 'axios'

// Error handling utilities
export class BuilderAPIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public details?: any,
    public isProjectNotFound: boolean = false,
    public isNoChanges: boolean = false
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
    
    // Check for "No changes to commit" responses - these are not really errors
    const isNoChanges: boolean = 
      statusCode === 400 && 
      details && 
      ((typeof details === 'object' && 
        ((details.message && details.message.includes('No changes to commit')) || 
         (details.error && details.error.includes('No changes to commit')) || 
         (details.detail && details.detail.includes('No changes to commit')))) ||
       (typeof details === 'string' && details.includes('No changes to commit')));

    // Log detailed information for 400 Bad Request errors for debugging
    if (statusCode === 400) {
      // Don't log "No changes to commit" as errors since they're not really errors
      if (isNoChanges) {
        console.log('Version control info:', {
          message: 'No changes to commit detected',
          url: axiosError.config?.url,
          method: axiosError.config?.method
        });
      } else {
        console.error('Bad Request Error Details:', {
          url: axiosError.config?.url,
          method: axiosError.config?.method,
          requestData: axiosError.config?.data ? JSON.parse(axiosError.config.data as string) : null,
          responseData: details,
          headers: axiosError.config?.headers
        });
      }
      
      // Construct a detailed error message
      let errorMsg = 'Bad Request: ';
      
      if (details && typeof details === 'object') {
        // Extract specific field errors if available
        if (details.file_path) {
          errorMsg += `File path error: ${details.file_path}. `;
        }
        if (details.description) {
          errorMsg += `Description error: ${details.description}. `;
        }
        if (details.error) {
          errorMsg += details.error;
        } else if (details.detail) {
          errorMsg += details.detail;
        } else if (details.message) {
          errorMsg += details.message;
        }
      } else if (details && typeof details === 'string') {
        errorMsg += details;
      }
      
      return new BuilderAPIError(
        errorMsg,
        statusCode,
        details,
        false,
        isNoChanges
      );
    }

    // Return early if no status code is available
    if (!statusCode) {
      return new BuilderAPIError(
        details?.message || axiosError.message || 'Network error occurred',
        undefined,
        details,
        false,
        false
      )
    }

    if (statusCode === 401) {
      return new BuilderAPIError('Session expired. Please log in again.', statusCode, details, false, false)
    }
    
    if (statusCode === 403) {
      return new BuilderAPIError('You do not have permission to perform this action.', statusCode, details, false, false)
    }

    if (statusCode === 404) {
      return new BuilderAPIError('The requested resource was not found.', statusCode, details, false, false)
    }

    if (statusCode === 429) {
      return new BuilderAPIError('API rate limit exceeded. Please try again later.', statusCode, details, false, false)
    }

    if (statusCode >= 500) {
      // Check if the server returned HTML instead of JSON
      if (typeof details === 'string' && details.includes('<!DOCTYPE html>')) {
        console.error('Server error returned HTML instead of JSON', details.substring(0, 200));
        return new BuilderAPIError(
          'Server error occurred. The API returned an error page instead of proper JSON response.',
          statusCode,
          { htmlResponse: true },
          false,
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
      
      return new BuilderAPIError(errorMessage, statusCode, details, false, false)
    }

    return new BuilderAPIError(
      details?.message || axiosError.message || 'An unknown error occurred',
      statusCode,
      details,
      false,
      isNoChanges
    )
  }

  if (error instanceof Error) {
    // Check if this is a "No changes to commit" error message
    const isNoChanges: boolean = error.message ? error.message.includes('No changes to commit') : false;
    return new BuilderAPIError(error.message, undefined, undefined, false, isNoChanges)
  }

  return new BuilderAPIError('An unknown error occurred', undefined, undefined, false, false)
}