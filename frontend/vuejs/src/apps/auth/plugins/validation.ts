import { configure, defineRule } from 'vee-validate'
import { required, min, max, email, confirmed } from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'
import type { App } from 'vue'

// Define base rules
defineRule('required', required)
defineRule('min', min)
defineRule('max', max)
defineRule('email', email)
defineRule('confirmed', confirmed)

// Custom username rule
defineRule('username', (value: string) => {
  if (!value) return true
  if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
    return 'Username can only contain letters, numbers, underscores and hyphens'
  }
  return true
})

// Add password rule
defineRule('password', (value: string) => {
  if (!value) return true
  if (value.length < 8) {
    return 'Password must be at least 8 characters'
  }
  return true
})

// Create a plugin object with install function
export const validationPlugin = {
  install: (app: App) => {
    configure({
      validateOnInput: false,
      validateOnBlur: false,
      validateOnChange: false,
      validateOnModelUpdate: false,
      generateMessage: localize('en', {
        messages: {
          required: 'This field is required',
          confirmed: 'Passwords do not match',
          email: 'Please enter a valid email address',
          password: 'Password must be at least 8 characters'
        }
      })
    })
  }
}

export { defineRule }
