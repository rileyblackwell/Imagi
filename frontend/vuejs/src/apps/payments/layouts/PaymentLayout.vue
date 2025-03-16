<!-- Payment layout with modern styling -->
<template>
  <DefaultLayout>
    <!-- Main Content with enhanced background -->
    <div class="payment-layout min-h-screen bg-dark-950">
      <!-- Decorative Elements -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Animated gradient orbs -->
        <div class="absolute top-[10%] left-[5%] w-[800px] h-[800px] rounded-full bg-primary-600/5 blur-[150px] animate-pulse-slow"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px] animate-pulse-slow animation-delay-150"></div>
        
        <!-- Grid pattern overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>
      
      <main class="relative z-10 min-h-screen py-8 md:py-16">
        <slot></slot>
      </main>
    </div>
  </DefaultLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'

export default defineComponent({
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
})
</script>

<style scoped>
/* Animation for background orbs */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

.animation-delay-150 {
  animation-delay: 150ms;
}

/* Noise texture background */
.bg-noise {
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='1'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 200px;
}
</style> 