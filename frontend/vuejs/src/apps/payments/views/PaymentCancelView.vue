<!-- Checkout canceled — on the Spotlight stage (class lists in
     ../layouts/payStage.ts). -->
<template>
  <PaymentLayout>
    <div class="editorial payment-cancel-view">
      <section :class="pay.stage">
        <div class="sl-spot" aria-hidden="true"></div>
        <div class="sl-dots" aria-hidden="true"></div>

        <div class="pay-rise" :class="pay.inner">
          <div class="text-sl-wait" :class="pay.mark"><i class="fas fa-arrow-rotate-left" aria-hidden="true"></i></div>
          <h1 class="sl-display" :class="pay.title">Payment cancelled</h1>
          <p class="sl-lede" :class="pay.lede">
            Your payment has been cancelled and you have not been charged.
          </p>

          <div :class="pay.card">
            <p class="m-0">
              If you encountered any issues or have questions about our payment process, please contact our support team.
            </p>
          </div>

          <div :class="pay.actions">
            <router-link to="/payments/pricing" class="btn-primary">
              <i class="fas fa-redo"></i>
              <span>Try again</span>
            </router-link>
            <router-link to="/" class="btn-outline">
              <i class="fas fa-home"></i>
              <span>Back to home</span>
            </router-link>
          </div>
        </div>
      </section>
    </div>
  </PaymentLayout>
</template>

<script setup lang="ts">
import PaymentLayout from '../layouts/PaymentLayout.vue'
import { pay } from '../layouts/payStage'
// No special logic needed for the cancel page
</script>
