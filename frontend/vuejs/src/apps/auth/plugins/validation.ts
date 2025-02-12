import { configure, defineRule } from 'vee-validate'
import { required, email } from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'
import type { App } from 'vue'

// Define base rules
defineRule('required', required)
defineRule('email', email)

// Simple username validation
defineRule('username', (value: string) => {
  if (!value) return true
  if (value.length < 1) return 'Username is required'
  return true
})

// Add terms agreement validation
defineRule('terms', (value: boolean) => {
  if (!value) {
    return 'You must agree to the Terms of Service and Privacy Policy'
  }
  return true
})

// Registration specific password validation
defineRule('registration_password', (value: string) => {
  if (!value) return 'Password is required'
  if (value.length < 8) return 'Password must be at least 8 characters'
  if (!/[A-Z]/.test(value)) return 'Password must contain at least one uppercase letter'
  if (!/[a-z]/.test(value)) return 'Password must contain at least one lowercase letter'
  if (!/[0-9]/.test(value)) return 'Password must contain at least one number'
  return true
})

defineRule('password_confirmation', (value: string, [target]: string[]) => {
  if (value !== target) {
    return 'Passwords must match'
  }
  return true
})

// Add login-specific validation rules
defineRule('login_username', (value: string) => {
  if (!value?.trim()) return 'Username is required'
  return true
})

defineRule('login_password', (value: string) => {
  if (!value?.trim()) return 'Password is required'
  return true
})

// Expand error messages to include login-specific messages
const errorMessages = {
  // Registration errors
  'UNIQUE constraint failed: auth_user.username': 'This username is already taken. Please try another one.',
  // Login errors
  'Unable to log in with provided credentials.': 'Invalid username or password. Please try again.',
  'Not found.': 'Account not found. Please check your username.',
  'Authentication credentials were not provided.': 'Please enter your login credentials.',
  'Invalid credentials': 'Username or password is incorrect',
  'Login failed: No token received': 'Unable to log in. Please try again.',
  'Network Error': 'Unable to connect to server. Please check your internet connection.',
  'Login failed: Please try again': 'Login failed. Please try again later.',
  'Login failed: Invalid response format': 'Unable to complete login. Please try again.',
  'Invalid server response: Missing token': 'Unable to complete login. Please try again.',
  'default': 'An unexpected error occurred. Please try again.'
} as const

export const formatAuthError = (error: unknown, context: 'login' | 'register' = 'login'): string => {
  if (error instanceof Error) {
    const message = error.message
    const formattedMessage = errorMessages[message as keyof typeof errorMessages]
    return formattedMessage || message
  }
  
  return errorMessages.default
}

export const validationPlugin = {
  install: (app: App) => {
    configure({
      validateOnInput: true,
      validateOnBlur: true,
      validateOnChange: true,
      validateOnModelUpdate: true,
      generateMessage: localize('en', {
        messages: {
          required: 'This field is required',
          email: 'Please enter a valid email address',
          terms: 'You must agree to the Terms of Service and Privacy Policy',
          registration_password: 'Password does not meet requirements',
          password_confirmation: 'Passwords must match',
          username: 'Please enter a valid username',
          login_username: 'Username is required',
          login_password: 'Password is required'
        }
      })
    })
  }
}

export { defineRule, errorMessages }
