<!-- Payment layout with clean minimal styling -->
<template>
  <DefaultLayout>
    <!-- Main Content -->
    <div class="payment-layout min-h-screen">
      <main class="relative min-h-screen">
        <slot></slot>
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent, onMounted, computed } from 'vue'
import { DefaultLayout } from '@/shared/layouts'

export default defineComponent({
  name: 'PaymentLayout',
  components: {
    DefaultLayout
  },
  data() {
    return {
      stripeLoading: false
    }
  },
  computed: {
    stripePublicKey() {
      return import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY
    }
  },
  mounted() {
    // Load Stripe.js if not already loaded
    this.loadStripeJs()
  },
  methods: {
    loadStripeJs() {
      if (window.Stripe) {
        // console.log('Stripe already loaded')
        this.stripeLoading = true
        this.stripe = window.Stripe(this.stripePublicKey)
        return Promise.resolve()
      }
      
      if (this.stripeLoading) {
        // console.log('Stripe loading in progress')
        return Promise.resolve()
      }
      
      this.stripeLoading = true
      
      return new Promise((resolve, reject) => {
        const script = document.createElement('script')
        script.src = 'https://js.stripe.com/v3/'
        script.async = true
        script.onload = () => {
          this.stripeLoading = false
          // console.log('Stripe.js loaded successfully')
          this.stripe = window.Stripe(this.stripePublicKey)
          resolve()
        }
        script.onerror = (error) => {
          this.stripeLoading = false
          // console.error('Failed to load Stripe.js:', error)
          reject(error)
        }
        
        document.head.appendChild(script)
      })
    }
  }
})
</script>

<style scoped>
/* Minimal clean styling */
.payment-layout {
  /* All styling handled by parent components */
}
</style> 