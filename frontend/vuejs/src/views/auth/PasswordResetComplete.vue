<template>
  <div class="reset-complete-page">
    <div class="reset-complete-container">
      <div class="success-message">
        <i class="fas fa-check-circle"></i>
        <h1>Password Reset Complete</h1>
        <p>Your password has been successfully reset.</p>
        <p>You can now log in with your new password.</p>
      </div>
      
      <BaseButton
        variant="primary"
        block
        @click="goToLogin"
      >
        Go to Login
      </BaseButton>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import BaseButton from '@/components/common/BaseButton.vue'

const router = useRouter()

function goToLogin() {
  router.push('/login')
}
</script>

<style scoped>
.reset-complete-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
  background: var(--color-background-alt);
}

.reset-complete-container {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-xl);
  background: var(--color-background);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
}

.success-message {
  text-align: center;
  color: var(--color-success);
  margin-bottom: var(--spacing-xl);
}

.success-message i {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-md);
}

.success-message h1 {
  color: var(--color-text);
  margin-bottom: var(--spacing-md);
}

.success-message p {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-sm);
}
</style> 