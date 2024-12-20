<template>
  <div class="reset-confirm-page">
    <div class="reset-confirm-container">
      <h1>Set New Password</h1>
      <p class="lead">Please enter your new password below</p>
      
      <form v-if="!success" @submit.prevent="handleSubmit" class="reset-confirm-form">
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
          Set New Password
        </BaseButton>
      </form>
      
      <div v-else class="success-message">
        <i class="fas fa-check-circle"></i>
        <p>Your password has been successfully reset.</p>
        <p>Redirecting you to confirmation page...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'
import FormInput from '@/components/common/FormInput.vue'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { confirmPasswordReset } = useAuth()

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
    await confirmPasswordReset({
      token: route.query.token,
      password: form.value.password
    })
    success.value = true
    setTimeout(() => {
      router.push('/password-reset-complete')
    }, 3000)
  } catch (err) {
    error.value = err.message || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.reset-confirm-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
}

.reset-confirm-container {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: var(--color-background);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.reset-confirm-container h1 {
  margin-bottom: var(--spacing-xs);
  text-align: center;
}

.lead {
  text-align: center;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
}

.reset-confirm-form {
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
</style> 