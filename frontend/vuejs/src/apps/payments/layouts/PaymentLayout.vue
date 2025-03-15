<!-- Payment layout with shared components -->
<template>
  <DefaultLayout>
    <!-- Main Content -->
    <div class="payment-layout min-h-screen bg-gradient-to-b from-dark-950 to-dark-900">
      <!-- Decorative Elements -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Gradient orbs -->
        <div class="absolute top-[10%] left-[5%] w-[800px] h-[800px] rounded-full bg-primary-500/5 blur-[120px] animate-float"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[600px] h-[600px] rounded-full bg-violet-500/5 blur-[100px] animate-float-delay"></div>
        <!-- Grid pattern overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>
      
      <main class="relative z-10 min-h-screen py-16">
        <slot></slot>
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { DefaultLayout } from '@/shared/layouts'

export default {
  name: 'PaymentLayout',
  components: {
    DefaultLayout
  },
  mounted() {
    // Load Stripe.js if not already loaded
    if (!window.Stripe && !document.querySelector('script[src*="stripe.com"]')) {
      const script = document.createElement('script')
      script.src = 'https://js.stripe.com/v3/'
      script.async = true
      script.defer = true
      script.addEventListener('load', () => {
        console.log('Stripe.js loaded successfully')
      })
      script.addEventListener('error', (error) => {
        console.error('Failed to load Stripe.js:', error)
      })
      document.head.appendChild(script)
    }
  }
}
</script>

<style scoped>
/* Noise texture */
.bg-noise {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.15'/%3E%3C/svg%3E");
}

/* Floating animations for background elements */
@keyframes float {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(-15px, 15px) rotate(1deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}

@keyframes float-delay {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(15px, -15px) rotate(-1deg); }
  100% { transform: translate(0, 0) rotate(0deg); }
}

.animate-float {
  animation: float 20s ease-in-out infinite;
}

.animate-float-delay {
  animation: float-delay 25s ease-in-out infinite;
}

/* Background color overrides */
.bg-dark-950 {
  background-color: rgba(9, 11, 17, 0.95);
}

.from-dark-950 {
  --tw-gradient-from: rgba(9, 11, 17, 0.95);
}

.to-dark-950 {
  --tw-gradient-to: rgba(9, 11, 17, 0.95);
}
</style> 