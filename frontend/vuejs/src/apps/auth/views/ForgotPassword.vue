<template>
  <div class="forgot-password-page">
    <div class="forgot-password-container">
      <h1>Reset Password</h1>
      <p class="lead">Enter your email to receive password reset instructions</p>
      
      <form v-if="!success" @submit.prevent="handleSubmit" class="forgot-password-form">
        <FormInput
          v-model="email"
          type="email"
          label="Email"
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
          Send Reset Link
        </BaseButton>
      </form>
      
      <div v-else class="success-message">
        <i class="fas fa-check-circle"></i>
        <p>Password reset instructions have been sent to your email.</p>
        <p>Please check your inbox and follow the instructions to reset your password.</p>
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

<script setup>
import { ref } from 'vue'
import BaseButton from '@/components/common/BaseButton.vue'
import FormInput from '@/components/common/FormInput.vue'
import { useAuth } from '@/composables/useAuth'

const { sendPasswordResetEmail } = useAuth()

const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

async function handleSubmit() {
  loading.value = true
  error.value = ''
  success.value = false
  
  try {
    await sendPasswordResetEmail(email.value)
    success.value = true
  } catch (err) {
    error.value = err.message || 'Failed to send reset email'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.forgot-password-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
}

.forgot-password-container {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: var(--color-background);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.forgot-password-container h1 {
  margin-bottom: var(--spacing-xs);
  text-align: center;
}

.lead {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
}

.forgot-password-form {
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