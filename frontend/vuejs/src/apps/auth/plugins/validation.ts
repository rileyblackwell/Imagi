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

// Add error message mapping
const errorMessages = {
  'UNIQUE constraint failed: auth_user.username': 'This username is already taken. Please try another one.',
  'default': 'An unexpected error occurred during registration'
} as const

export const formatRegistrationError = (error: unknown): string => {
  if (error instanceof Error) {
    const message = error.message
    return errorMessages[message as keyof typeof errorMessages] || message
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
          username: 'Please enter a valid username'
        }
      })
    })
  }
}

export { defineRule, errorMessages }
