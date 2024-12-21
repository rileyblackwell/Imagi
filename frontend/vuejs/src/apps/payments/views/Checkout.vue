<template>
  <div class="checkout-container">
    <h1>Checkout</h1>
    <div class="payment-form">
      <base-card>
        <template #header>
          <h2>Payment Details</h2>
        </template>
        <div class="payment-options">
          <base-input
            v-model="cardNumber"
            label="Card Number"
            placeholder="1234 5678 9012 3456"
            type="text"
          />
          <div class="card-details">
            <base-input
              v-model="expiryDate"
              label="Expiry Date"
              placeholder="MM/YY"
              type="text"
              class="expiry"
            />
            <base-input
              v-model="cvv"
              label="CVV"
              placeholder="123"
              type="text"
              class="cvv"
            />
          </div>
          <base-input
            v-model="cardName"
            label="Name on Card"
            placeholder="John Doe"
            type="text"
          />
        </div>
        <template #footer>
          <base-button @click="processPayment" variant="primary" block>
            Pay Now
          </base-button>
        </template>
      </base-card>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Checkout',
  setup() {
    const router = useRouter()
    const cardNumber = ref('')
    const expiryDate = ref('')
    const cvv = ref('')
    const cardName = ref('')

    const processPayment = async () => {
      try {
        // TODO: Implement payment processing logic
        router.push({ name: 'PaymentSuccess' })
      } catch (error) {
        router.push({ name: 'PaymentCancel' })
      }
    }

    return {
      cardNumber,
      expiryDate,
      cvv,
      cardName,
      processPayment
    }
  }
}
</script>

<style scoped>
.checkout-container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.payment-form {
  margin-top: 2rem;
}

.card-details {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 1rem 0;
}

.payment-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style> 