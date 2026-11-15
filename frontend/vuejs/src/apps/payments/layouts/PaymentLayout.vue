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
