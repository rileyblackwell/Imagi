<!-- Payment layout with shared components -->
<template>
  <BaseLayout>
    <!-- Navigation -->
    <BaseNavbar />

    <!-- Main Content -->
    <main class="min-h-screen">
      <router-view></router-view>
    </main>

    <!-- Footer -->
    <BaseFooter />
  </BaseLayout>
</template>

<script>
import { BaseLayout } from '@/shared/layouts'
import { BaseNavbar, BaseFooter } from '@/shared/components'

export default {
  name: 'PaymentLayout',
  components: {
    BaseLayout,
    BaseNavbar,
    BaseFooter
  },
  mounted() {
    // Load Stripe.js
    if (!window.Stripe) {
      const script = document.createElement('script')
      script.src = 'https://js.stripe.com/v3/'
      script.async = true
      document.head.appendChild(script)
    }
  }
}
</script>

<style scoped>
.min-h-screen {
  min-height: 100vh;
  background: radial-gradient(
    circle at top right,
    rgba(0, 255, 204, 0.05),
    transparent 50%
  );
}
</style> 