<template>
  <div class="success-container">
    <div class="success-content">
      <base-card>
        <div class="success-message">
          <svg class="checkmark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 52">
            <circle class="checkmark-circle" cx="26" cy="26" r="25" fill="none"/>
            <path class="checkmark-check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
          </svg>
          <h1>Payment Successful!</h1>
          <p>Thank you for your purchase. Your payment has been processed successfully.</p>
          <base-button @click="goToDashboard" variant="primary">
            Go to Dashboard
          </base-button>
        </div>
      </base-card>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'PaymentSuccess',
  setup() {
    const router = useRouter()

    const goToDashboard = () => {
      router.push({ name: 'Dashboard' })
    }

    return {
      goToDashboard
    }
  }
}
</script>

<style scoped>
.success-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.success-content {
  max-width: 600px;
  width: 100%;
}

.success-message {
  text-align: center;
  padding: 2rem;
}

.success-message h1 {
  margin: 1.5rem 0;
  color: #4CAF50;
}

.success-message p {
  margin-bottom: 2rem;
  color: #666;
}

.checkmark {
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.checkmark-circle {
  stroke: #4CAF50;
  stroke-width: 2;
  stroke-dasharray: 166;
  stroke-dashoffset: 166;
  animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
}

.checkmark-check {
  stroke: #4CAF50;
  stroke-width: 2;
  stroke-dasharray: 48;
  stroke-dashoffset: 48;
  animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
}

@keyframes stroke {
  100% {
    stroke-dashoffset: 0;
  }
}
</style> 