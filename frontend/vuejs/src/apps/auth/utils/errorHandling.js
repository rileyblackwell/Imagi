export function formatAuthError(error, context = 'auth') {
  // Handle login-specific errors
  if (context === 'login') {
    // Handle 400 Bad Request
    if (error.response?.status === 400) {
      const errorData = error.response.data
      
      if (errorData.non_field_errors) {
        return errorData.non_field_errors[0]
      }
      if (errorData.password) {
        return 'The password you entered is incorrect'
      }
      if (errorData.username) {
        return 'No account found with this username'
      }
      
      return 'Invalid username or password'
    }

    // Handle other status codes
    if (error.response?.status === 401) {
      return 'Invalid credentials. Please check your username and password.'
    }
    if (error.response?.status === 429) {
      return 'Too many login attempts. Please try again later.'
    }
  }

  // Handle network errors
  if (error.message === 'Network Error') {
    return 'Unable to connect to server. Please check your connection.'
  }

  // Return error message or fallback
  return error.message || 'An unexpected error occurred. Please try again.'
}
