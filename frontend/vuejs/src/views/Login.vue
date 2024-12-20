<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Welcome Back</h1>
        <p class="auth-subtitle">Sign in to continue building amazing things</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="app-form-group">
          <label for="username" class="app-form-label">Username</label>
          <input
            type="text"
            id="username"
            v-model="form.username"
            class="app-form-input"
            required
            autocomplete="username"
          />
        </div>

        <div class="app-form-group">
          <label for="password" class="app-form-label">Password</label>
          <input
            type="password"
            id="password"
            v-model="form.password"
            class="app-form-input"
            required
            autocomplete="current-password"
          />
        </div>

        <div class="auth-options">
          <div class="form-check">
            <input
              type="checkbox"
              id="remember"
              v-model="form.remember"
              class="form-check-input"
            />
            <label for="remember" class="form-check-label">Remember me</label>
          </div>
          <router-link to="/password-reset" class="link">Forgot password?</router-link>
        </div>

        <div class="auth-actions">
          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            <span v-if="loading" class="app-loading">
              <span class="app-loading-spinner"></span>
              Signing in...
            </span>
            <span v-else>
              <i class="fas fa-sign-in-alt"></i>
              Sign In
            </span>
          </button>
        </div>

        <div v-if="error" class="app-alert app-alert-danger">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>
      </form>

      <div class="auth-footer">
        <p class="auth-footer-text">
          Don't have an account?
          <router-link to="/register" class="link">Sign up</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'LoginView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    
    const form = reactive({
      username: '',
      password: '',
      remember: false
    })
    
    const handleSubmit = async () => {
      try {
        loading.value = true
        error.value = ''
        
        await store.dispatch('auth/login', {
          username: form.username,
          password: form.password
        })
        
        router.push('/dashboard')
      } catch (err) {
        error.value = err.response?.data?.detail || 'Login failed. Please try again.'
      } finally {
        loading.value = false
      }
    }
    
    return {
      form,
      loading,
      error,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--app-spacing-lg);
}

.auth-card {
  background: var(--app-bg-glass);
  border: 1px solid var(--app-border-light);
  border-radius: 12px;
  padding: var(--app-spacing-xl);
  width: 100%;
  max-width: 400px;
}

.auth-header {
  text-align: center;
  margin-bottom: var(--app-spacing-xl);
}

.auth-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: var(--app-spacing-sm);
  background: var(--global-highlight-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.auth-subtitle {
  color: var(--global-muted-text-color);
}

.auth-form {
  margin-bottom: var(--app-spacing-lg);
}

.auth-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--app-spacing-lg);
}

.form-check {
  display: flex;
  align-items: center;
  gap: var(--app-spacing-sm);
}

.form-check-input {
  width: 1rem;
  height: 1rem;
  margin: 0;
}

.form-check-label {
  color: var(--global-muted-text-color);
  font-size: 0.875rem;
}

.auth-actions {
  margin-bottom: var(--app-spacing-lg);
}

.auth-footer {
  text-align: center;
  border-top: 1px solid var(--app-border-light);
  padding-top: var(--app-spacing-lg);
}

.auth-footer-text {
  color: var(--global-muted-text-color);
  margin: 0;
}

/* Loading state */
.w-100 {
  width: 100%;
}
</style> 