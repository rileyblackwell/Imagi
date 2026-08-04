<!-- Payment layout - warm porcelain editorial canvas shared by all payment pages -->
<template>
  <DefaultLayout>
    <!-- Main Content -->
    <div class="payment-layout page-canvas brand-selection crisp-text relative min-h-screen font-body transition-colors duration-500">
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



<!-- Unscoped: brand-tinted text selection on payment pages -->
 