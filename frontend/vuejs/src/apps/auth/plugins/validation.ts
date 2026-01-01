import { configure, defineRule } from 'vee-validate'
import { required, email } from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'
import type { App } from 'vue'

// Define base rules
defineRule('required', () => true)
defineRule('email', (value: string) => {
  if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
    return 'Please enter a valid email address'
  }
  return true
})

// Username validation - must be at least 3 characters, alphanumeric with underscores allowed
defineRule('username', (value: string) => {
  if (!value) return true // Let required rule handle empty values
  if (value.length < 3) return 'Username must be at least 3 characters'
  if (value.length > 150) return 'Username must be less than 150 characters'
  if (!/^[a-zA-Z0-9_]+$/.test(value)) return 'Username can only contain letters, numbers, and underscores'
  return true
})

// Add terms agreement validation
defineRule('terms', () => true)

// Registration specific password validation
defineRule('registration_password', (value: string) => {
  if (value && value.length < 8) return 'Password must be at least 8 characters'
  if (value && !/[A-Z]/.test(value)) return 'Password must contain at least one uppercase letter'
  if (value && !/[a-z]/.test(value)) return 'Password must contain at least one lowercase letter'
  if (value && !/[0-9]/.test(value)) return 'Password must contain at least one number'
  return true
})

defineRule('password_confirmation', (value: string, [target]: string[]) => {
  if (value && target && value !== target) {
    return 'Passwords must match'
  }
  return true
})

// Add login-specific validation rules
defineRule('login_username', () => true)

defineRule('login_password', () => true)

// Expand error messages to include login-specific messages
const errorMessages = {
  // Registration errors
  'This username is already taken. Please choose another one.': 'This username is already taken. Please try another one.',
  'A user is already registered with this e-mail address.': 'This email is already registered. Please use another one or sign in.',
  'Password must be at least 8 characters long': 'Password must be at least 8 characters long.',
  'Passwords don\'t match': 'Passwords don\'t match. Please make sure they are identical.',
  'Unable to complete registration. Please try again.': 'Unable to complete registration. Please try again.',
  
  // Login errors
  'No account found with this username': 'No account found with this username. Please check your spelling or create an account.',
  'Invalid password. Please try again': 'Incorrect password. Please try again.',
  'This account has been disabled': 'This account has been disabled. Please contact support.',
  'Unable to log in with provided credentials.': 'Invalid username or password. Please try again.',
  'Username is required': 'Username is required.',
  'Password is required': 'Password is required.',
  'Not found.': 'Account not found. Please check your username.',
  'Authentication credentials were not provided.': 'Please enter your login credentials.',
  'Invalid credentials': 'Username or password is incorrect.',
  'Login failed. Please try again later': 'Login failed. Please try again later.',
  'Login failed: No token received': 'Unable to log in. Please try again.',
  'Network Error': 'Unable to connect to server. Please check your internet connection.',
  'Login failed: Please try again': 'Login failed. Please try again later.',
  'Login failed: Invalid response format': 'Unable to complete login. Please try again.',
  'Invalid server response: Missing token': 'Unable to complete login. Please try again.',
  'default': 'An unexpected error occurred. Please try again.'
} as const

export const formatAuthError = (error: unknown, context: 'login' | 'register' = 'login'): string => {
  if (!error) return errorMessages.default
  
  if (error instanceof Error) {
    const message = error.message
    
    // Check if this is an axios error with a response
    const axiosError = error as any
    if (axiosError?.response?.data) {
      const responseData = axiosError.response.data
      
      // Check for different error formats
      if (responseData.error) {
        return errorMessages[responseData.error as keyof typeof errorMessages] || responseData.error
      }
      
      if (responseData.detail) {
        if (typeof responseData.detail === 'object') {
          // Convert detailed validation errors to readable messages
          const errorMessages = []
          
          for (const [field, message] of Object.entries(responseData.detail)) {
            if (field === 'non_field_errors' || field === 'error') {
              errorMessages.push(message)
            } else {
              errorMessages.push(`${field}: ${message}`)
            }
          }
          
          return errorMessages.join('\n')
        }
        
        return responseData.detail
      }
      
      // Handle non_field_errors array
      if (responseData.non_field_errors && Array.isArray(responseData.non_field_errors)) {
        return responseData.non_field_errors[0]
      }
    }
    
    // Check message against our known error messages
    const formattedMessage = errorMessages[message as keyof typeof errorMessages]
    return formattedMessage || message
  }
  
  // If error is just a string
  if (typeof error === 'string') {
    return errorMessages[error as keyof typeof errorMessages] || error
  }
  
  return errorMessages.default
}

export const validationPlugin = {
  install: (app: App) => {
    configure({
      validateOnInput: false,
      validateOnBlur: false,
      validateOnChange: false,
      validateOnModelUpdate: false,
      generateMessage: () => '',
    })
  }
}

export { defineRule, errorMessages }
