<template>
  <div class="auth-form-container">
    <div class="auth-form-card">
      <div class="auth-form-header">
        <h1>Create Account</h1>
        <p>Join Imagi and start building amazing web applications</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="form-group" :class="{ 'has-error': errors.username }">
          <div class="input-wrapper">
            <input
              v-model="form.username"
              type="text"
              class="form-input"
              placeholder="Username"
              required
            />
            <label class="floating-label">Username</label>
          </div>
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.email }">
          <div class="input-wrapper">
            <input
              v-model="form.email"
              type="email"
              class="form-input"
              placeholder="Email"
              required
            />
            <label class="floating-label">Email</label>
          </div>
          <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.password }">
          <div class="input-wrapper">
            <div class="password-input">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="Password"
                required
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="togglePassword"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <label class="floating-label">Password</label>
          </div>
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div class="form-group" :class="{ 'has-error': errors.confirmPassword }">
          <div class="input-wrapper">
            <div class="password-input">
              <input
                v-model="form.confirmPassword"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                placeholder="Confirm Password"
                required
              />
              <button 
                type="button" 
                class="password-toggle"
                @click="togglePassword"
              >
                <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
              </button>
            </div>
            <label class="floating-label">Confirm Password</label>
          </div>
          <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
        </div>

        <div class="form-group terms">
          <label class="checkbox-label">
            <input
              v-model="form.agreeToTerms"
              type="checkbox"
              required
            />
            <span>I agree to the <router-link to="/terms">Terms of Service</router-link> and <router-link to="/privacy">Privacy Policy</router-link></span>
          </label>
          <span v-if="errors.agreeToTerms" class="error-message">{{ errors.agreeToTerms }}</span>
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="isLoading">
          <span v-if="isLoading">
            <i class="fas fa-spinner fa-spin"></i>
            Creating Account...
          </span>
          <span v-else>Create Account</span>
        </button>

        <div class="auth-links">
          <p>Already have an account? <router-link to="/auth/login">Sign In</router-link></p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'RegisterPage',
  setup() {
    const store = useStore()
    const router = useRouter()
    const isLoading = ref(false)
    const errors = reactive({})
    const showPassword = ref(false)

    const form = reactive({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      agreeToTerms: false
    })

    const togglePassword = () => {
      showPassword.value = !showPassword.value
    }

    const validateForm = () => {
      const newErrors = {}

      if (!form.username) {
        newErrors.username = 'Username is required'
      }

      if (!form.email) {
        newErrors.email = 'Email is required'
      } else if (!/\S+@\S+\.\S+/.test(form.email)) {
        newErrors.email = 'Please enter a valid email address'
      }

      if (!form.password) {
        newErrors.password = 'Password is required'
      } else if (form.password.length < 8) {
        newErrors.password = 'Password must be at least 8 characters long'
      }

      if (!form.confirmPassword) {
        newErrors.confirmPassword = 'Please confirm your password'
      } else if (form.password !== form.confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match'
      }

      if (!form.agreeToTerms) {
        newErrors.agreeToTerms = 'You must agree to the Terms of Service and Privacy Policy'
      }

      Object.assign(errors, newErrors)
      return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async () => {
      if (!validateForm()) return

      isLoading.value = true
      try {
        await store.dispatch('auth/register', {
          username: form.username,
          email: form.email,
          password: form.password
        })
        router.push('/dashboard')
      } catch (error) {
        if (error.response?.data) {
          Object.assign(errors, error.response.data)
        } else {
          errors.general = 'An error occurred during registration'
        }
      } finally {
        isLoading.value = false
      }
    }

    return {
      form,
      errors,
      isLoading,
      showPassword,
      togglePassword,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.auth-form-container {
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.auth-form-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  width: 100%;
  max-width: 480px;
  padding: 2.5rem;
}

.auth-form-header {
  text-align: center;
  margin-bottom: 2.5rem;
}

.auth-form-header h1 {
  color: #1e293b;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.auth-form-header p {
  color: #64748b;
  font-size: 1rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  position: relative;
}

.input-wrapper {
  position: relative;
}

.password-input {
  position: relative;
}

.password-toggle {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #1e293b;
}

.form-input {
  width: 100%;
  padding: 1rem;
  padding-right: 2.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: all 0.2s;
  background: white;
}

.form-input:focus {
  border-color: #6366f1;
  outline: none;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.floating-label {
  position: absolute;
  left: 1rem;
  top: 1rem;
  pointer-events: none;
  transition: all 0.2s;
  color: #64748b;
  background: white;
  padding: 0 0.25rem;
}

.form-input:focus + .floating-label,
.form-input:not(:placeholder-shown) + .floating-label {
  transform: translateY(-1.4rem) scale(0.85);
  color: #6366f1;
}

.has-error .form-input {
  border-color: #ef4444;
}

.has-error .floating-label {
  color: #ef4444;
}

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-top: 0.5rem;
  display: block;
}

.terms {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  color: #64748b;
  font-size: 0.875rem;
}

.checkbox-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  margin-top: 0.25rem;
}

.checkbox-label a {
  color: #6366f1;
  text-decoration: none;
}

.checkbox-label a:hover {
  text-decoration: underline;
}

.btn {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #6366f1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4f46e5;
}

.btn-primary:disabled {
  background-color: #c7d2fe;
  cursor: not-allowed;
}

.auth-links {
  text-align: center;
  margin-top: 1.5rem;
  color: #64748b;
}

.auth-links a {
  color: #6366f1;
  text-decoration: none;
  font-weight: 500;
}

.auth-links a:hover {
  text-decoration: underline;
}

@media (max-width: 640px) {
  .auth-form-container {
    padding: 1rem;
  }

  .auth-form-card {
    padding: 2rem;
  }

  .auth-form-header h1 {
    font-size: 1.75rem;
  }
}
</style> 