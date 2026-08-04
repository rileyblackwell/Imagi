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
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'

export default defineComponent({
  name: 'PaymentLayout',
  components: {
    DefaultLayout
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