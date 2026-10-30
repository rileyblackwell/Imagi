<!-- Payment layout — the Spotlight stage shared by the pricing page and the
     checkout return pages. The .spotlight root sits outside DefaultLayout so
     the navbar and footer take the stage's colours too. -->
<template>
  <div class="spotlight payment-root">
  <DefaultLayout minimal-nav>
    <div class="payment-layout brand-selection relative min-h-screen">
      <main class="relative min-h-screen">
        <slot></slot>
      </main>
    </div>
  </DefaultLayout>
  </div>
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

<!-- The checkout return pages' motion (their styling is Tailwind, in
     payStage.ts). Keyframe animations stay CSS; unscoped so the views, which
     render inside this layout's slot, can use them. -->
<style>
.payment-root .pay-spinner {
  animation: pay-spin 0.9s linear infinite;
}

@keyframes pay-spin {
  to { transform: rotate(360deg); }
}

.payment-root .pay-rise {
  animation: pay-rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes pay-rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: none; }
}

@media (prefers-reduced-motion: reduce) {
  .payment-root .pay-rise { animation: none; }
}
</style>
