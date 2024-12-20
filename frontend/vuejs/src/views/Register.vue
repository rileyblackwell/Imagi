<template>
  <div class="register-page">
    <div class="register-container">
      <h1>Create Account</h1>
      <p class="subtitle">Join Imagi and start building your projects</p>
      
      <form @submit.prevent="handleSubmit" class="register-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="form-control"
            :class="{ 'is-invalid': submitted && !form.username }"
            required
          />
          <div v-if="submitted && !form.username" class="invalid-feedback">
            Username is required
          </div>
        </div>
        
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="form-control"
            :class="{ 'is-invalid': submitted && !form.email }"
            required
          />
          <div v-if="submitted && !form.email" class="invalid-feedback">
            Email is required
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': submitted && !form.password }"
            required
          />
          <div v-if="submitted && !form.password" class="invalid-feedback">
            Password is required
          </div>
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">Confirm Password</label>
          <input
            id="confirmPassword"
            v-model="form.confirmPassword"
            type="password"
            class="form-control"
            :class="{ 'is-invalid': submitted && !passwordsMatch }"
            required
          />
          <div v-if="submitted && !passwordsMatch" class="invalid-feedback">
            Passwords must match
          </div>
        </div>
        
        <div class="form-group form-check">
          <input
            id="terms"
            v-model="form.acceptTerms"
            type="checkbox"
            class="form-check-input"
            :class="{ 'is-invalid': submitted && !form.acceptTerms }"
            required
          />
          <label class="form-check-label" for="terms">
            I agree to the <router-link to="/terms">Terms of Service</router-link> and
            <router-link to="/privacy">Privacy Policy</router-link>
          </label>
          <div v-if="submitted && !form.acceptTerms" class="invalid-feedback">
            You must accept the terms and conditions
          </div>
        </div>
        
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm mr-1"></span>
          Create Account
        </button>
        
        <div class="mt-3 text-center">
          <p>
            Already have an account?
            <router-link to="/login">Sign in</router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'

export default {
  name: 'RegisterView',
  
  setup() {
    const store = useStore()
    const router = useRouter()
    
    const form = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      acceptTerms: false
    })
    
    const submitted = ref(false)
    
    const loading = computed(() => store.state.auth.loading)
    const error = computed(() => store.state.auth.error)
    const passwordsMatch = computed(() => 
      form.value.password && form.value.password === form.value.confirmPassword
    )
    
    const handleSubmit = async () => {
      submitted.value = true
      
      if (!form.value.username || !form.value.email || !form.value.password || 
          !form.value.confirmPassword || !form.value.acceptTerms || !passwordsMatch.value) {
        return
      }
      
      try {
        await store.dispatch('auth/register', {
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
        
        router.push('/dashboard')
      } catch (err) {
        // Error is handled by the store
        console.error('Registration failed:', err)
      }
    }
    
    return {
      form,
      submitted,
      loading,
      error,
      passwordsMatch,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  padding: 2rem 0;
}

.register-container {
  width: 100%;
  max-width: 500px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 2rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 0.5rem;
}

.subtitle {
  text-align: center;
  color: #6c757d;
  margin-bottom: 2rem;
}

.register-form {
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  label {
    font-weight: 500;
    margin-bottom: 0.5rem;
  }
  
  .form-control {
    padding: 0.75rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    
    &:focus {
      border-color: #80bdff;
      box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
    }
  }
  
  .form-check {
    padding-left: 1.75rem;
    
    .form-check-input {
      margin-left: -1.75rem;
    }
  }
  
  .btn-primary {
    width: 100%;
    padding: 0.75rem;
    font-weight: 500;
    margin-top: 1rem;
  }
  
  .invalid-feedback {
    color: #dc3545;
    font-size: 0.875rem;
    margin-top: 0.25rem;
  }
}

a {
  color: #007bff;
  text-decoration: none;
  
  &:hover {
    text-decoration: underline;
  }
}
</style> 