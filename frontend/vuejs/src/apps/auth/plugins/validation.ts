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

// Custom password rule
defineRule('password', (value: string) => {
  if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(value)) {
    return 'Password must be at least 8 characters and contain uppercase, lowercase, number and special character'
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
      required: '{field} is required',
      confirmed: 'Passwords do not match',
      username: 'Username format is invalid',
      password: 'Password format is invalid'
    }
  })
})

export default configure
