<!-- Payment layout - warm porcelain editorial canvas shared by all payment pages -->
<template>
  <DefaultLayout>
    <!-- Main Content -->
    <div class="payment-layout relative min-h-screen font-body transition-colors duration-500">
      <!-- Grain texture over the whole canvas -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>
      <main class="relative z-10 min-h-screen">
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
/* One continuous warm-porcelain canvas; pages paint soft washes on top.
   The gradient ends on the footer's exact background (bg-white / dark #0a0a0a)
   so the page hands off seamlessly. */
.payment-layout {
  background: linear-gradient(180deg, #fdf9f2 0%, #faf7f1 45%, #ffffff 100%);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

:root.dark .payment-layout,
.dark .payment-layout {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0b0f 50%, #0a0a0a 100%);
}

/* Fine film grain keeps large soft gradients from banding and adds texture */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

:root.dark .grain-overlay,
.dark .grain-overlay {
  opacity: 0.05;
  mix-blend-mode: overlay;
}
</style>

<!-- Unscoped: brand-tinted text selection on payment pages -->
<style>
.payment-layout ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .payment-layout ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style> 