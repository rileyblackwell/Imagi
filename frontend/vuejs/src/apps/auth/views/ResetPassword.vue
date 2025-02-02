<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import FormInput from '@/components/common/FormInput.vue'
import { useAuthStore } from '@/apps/auth/store'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  password: '',
  confirmPassword: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleSubmit() {
  if (form.value.password !== form.value.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    await authStore.resetPassword({
      token: route.query.token,
      password: form.value.password
    })
    success.value = true
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (err) {
    error.value = err.message || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="reset-password-page">
    <div class="reset-password-container">
      <h1>Reset Password</h1>
      <p class="lead">Enter your new password below</p>
      
      <form v-if="!success" @submit.prevent="handleSubmit" class="reset-password-form">
        <FormInput
          v-model="form.password"
          type="password"
          label="New Password"
          required
        />
        
        <FormInput
          v-model="form.confirmPassword"
          type="password"
          label="Confirm New Password"
          required
        />
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <BaseButton
          type="submit"
          variant="primary"
          block
          :loading="loading"
        >
          Reset Password
        </BaseButton>
      </form>
      
      <div v-else class="success-message">
        <i class="fas fa-check-circle"></i>
        <p>Your password has been successfully reset.</p>
        <p>Redirecting you to login...</p>
      </div>
      
      <div class="auth-footer">
        <p>
          Remember your password?
          <router-link to="/login">Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.reset-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
}

.reset-password-container {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: var(--color-background);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.reset-password-container h1 {
  margin-bottom: var(--spacing-xs);
  text-align: center;
}

.lead {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
}

.reset-password-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.error-message {
  color: var(--color-error);
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-md);
}

.success-message {
  text-align: center;
  color: var(--color-success);
  margin: var(--spacing-xl) 0;
}

.success-message i {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-md);
}

.success-message p {
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
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