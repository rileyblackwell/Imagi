<template>
  <div class="cancel-container">
    <div class="cancel-content">
      <base-card>
        <div class="cancel-message">
          <svg class="cancel-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
            <line x1="8" y1="8" x2="16" y2="16" stroke="currentColor" stroke-width="2"/>
            <line x1="16" y1="8" x2="8" y2="16" stroke="currentColor" stroke-width="2"/>
          </svg>
          <h1>Payment Cancelled</h1>
          <p>Your payment was cancelled. No charges have been made to your account.</p>
          <div class="actions">
            <base-button @click="tryAgain" variant="primary">
              Try Again
            </base-button>
            <base-button @click="goToDashboard" variant="secondary">
              Go to Dashboard
            </base-button>
          </div>
        </div>
      </base-card>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'PaymentCancel',
  setup() {
    const router = useRouter()

    const tryAgain = () => {
      router.push({ name: 'Checkout' })
    }

    const goToDashboard = () => {
      router.push({ name: 'Dashboard' })
    }

    return {
      tryAgain,
      goToDashboard
    }
  }
}
</script>

<style scoped>
.cancel-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.cancel-content {
  max-width: 600px;
  width: 100%;
}

.cancel-message {
  text-align: center;
  padding: 2rem;
}

.cancel-message h1 {
  margin: 1.5rem 0;
  color: #f44336;
}

.cancel-message p {
  margin-bottom: 2rem;
  color: #666;
}

.cancel-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  color: #f44336;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}
</style> 