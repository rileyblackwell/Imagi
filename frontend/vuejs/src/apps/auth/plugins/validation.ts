import { configure, defineRule } from 'vee-validate'
import { required, min, max, email, confirmed } from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'

// Define base rules
defineRule('required', required)
defineRule('min', min)
defineRule('max', max)
defineRule('email', email)
defineRule('confirmed', confirmed)

// Custom username rule - removed length requirements
defineRule('username', (value: string) => {
  if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
    return 'Username can only contain letters, numbers, underscores and hyphens'
  }
  return true
})

// Custom password rule - no requirements
defineRule('password', (value: string) => {
  if (!value) {
    return 'Password is required'
  }
  return true
})

// Configure VeeValidate
configure({
  validateOnInput: false, // Only validate on submit
  validateOnBlur: false, // Don't validate on blur
  validateOnChange: false, // Don't validate on change
  validateOnModelUpdate: false, // Don't validate on model update
  generateMessage: localize('en', {
    messages: {
      required: 'The {field} field is required',
      confirmed: 'The password confirmation does not match',
      username: 'Username must contain only letters, numbers, underscores or hyphens',
      password: 'Password is required',
      email: 'Please enter a valid email address',
      min: '{field} must be at least {length} characters',
      max: '{field} must not exceed {length} characters'
    }
  })
})

export default configure
