import { configure, defineRule } from 'vee-validate'
import { required, min, max, email, confirmed } from '@vee-validate/rules'
import { localize } from '@vee-validate/i18n'

// Define base rules
defineRule('required', required)
defineRule('min', min)
defineRule('max', max)
defineRule('email', email)
defineRule('confirmed', confirmed)

// Custom username rule
defineRule('username', (value: string) => {
  if (!/^[a-zA-Z0-9_-]{3,20}$/.test(value)) {
    return 'Username must be 3-20 characters and can only contain letters, numbers, underscores and hyphens'
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
  generateMessage: localize('en', {
    messages: {
      required: '{field} is required',
      min: '{field} must be at least {length} characters',
      max: '{field} must not exceed {length} characters',
      email: 'Please enter a valid email',
      confirmed: 'Passwords do not match',
      username: 'Username format is invalid',
      password: 'Password format is invalid'
    }
  }),
  validateOnInput: true
})

export default configure
