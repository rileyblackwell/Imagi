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
          terms: 'You must agree to the Terms of Service and Privacy Policy'
        }
      })
    })
  }
}

export { defineRule }
