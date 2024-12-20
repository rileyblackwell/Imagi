<template>
  <div class="register-page">
    <div class="register-container">
      <h1>Create Account</h1>
      <p class="lead">Join Imagi to start building amazing projects</p>
      
      <form @submit.prevent="handleSubmit" class="register-form">
        <FormInput
          v-model="form.name"
          type="text"
          label="Full Name"
          required
        />
        
        <FormInput
          v-model="form.email"
          type="email"
          label="Email"
          required
        />
        
        <FormInput
          v-model="form.password"
          type="password"
          label="Password"
          required
        />
        
        <FormInput
          v-model="form.confirmPassword"
          type="password"
          label="Confirm Password"
          required
        />
        
        <div class="terms-checkbox">
          <label>
            <input type="checkbox" v-model="form.agreeToTerms" required>
            I agree to the 
            <router-link to="/terms">Terms of Service</router-link>
            and
            <router-link to="/privacy">Privacy Policy</router-link>
          </label>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <BaseButton
          type="submit"
          variant="primary"
          block
          :loading="loading"
        >
          Create Account
        </BaseButton>
      </form>
      
      <div class="auth-footer">
        <p>
          Already have an account?
          <router-link to="/login">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import FormInput from '@/components/common/FormInput.vue'
import { useAuth } from '@/composables/useAuth'

defineOptions({
  name: 'RegisterView'
})

const router = useRouter()
const { register } = useAuth()

const form = ref({
  name: '',
  email: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false
})

const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  if (form.value.password !== form.value.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    await register(form.value)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.message || 'Failed to register'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
}

.register-container {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: var(--color-background);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.register-container h1 {
  margin-bottom: var(--spacing-xs);
  text-align: center;
}

.lead {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.terms-checkbox {
  margin: var(--spacing-sm) 0;
}

.terms-checkbox label {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-xs);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.terms-checkbox input[type="checkbox"] {
  margin-top: 0.2em;
}

.terms-checkbox a {
  color: var(--color-primary);
  text-decoration: none;
}

.terms-checkbox a:hover {
  text-decoration: underline;
}

.error-message {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
}

.auth-footer {
  margin-top: var(--spacing-xl);
  text-align: center;
}

.auth-footer p {
  color: var(--color-text-secondary);
}

.auth-footer a {
  color: var(--color-primary);
  text-decoration: none;
  margin-left: var(--spacing-xs);
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style> 