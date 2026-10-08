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

<!-- Unscoped: the checkout return pages (success, cancel) share this stage —
     a status mark in the light, a headline, and one card edged like the home
     page's prompt bar. Scoped to .payment-root so nothing leaks. -->
<style>
.payment-root .pay-stage {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  min-height: 100vh;
  padding: calc(3.5rem + clamp(56px, 8vw, 104px)) 0 clamp(72px, 10vw, 120px);
}

.payment-root .pay-stage__inner {
  max-width: 40rem;
  margin-inline: auto;
  padding-inline: clamp(16px, 4vw, 40px);
  text-align: center;
}

.payment-root .pay-mark {
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  margin: 0 auto 26px;
  border-radius: 20px;
  border: 1px solid var(--sl-line-strong);
  background: var(--sl-card-bg);
  box-shadow: var(--sl-card-shadow), 0 0 40px -8px var(--sl-glow);
  font-size: 22px;
  color: var(--sl-coral);
}

.payment-root .pay-mark--ok { color: var(--sl-ok); }
.payment-root .pay-mark--bad { color: var(--sl-bad); }
.payment-root .pay-mark--wait { color: var(--sl-wait); }

.payment-root .pay-title {
  font-size: clamp(38px, 6vw, 64px);
  line-height: 1;
  letter-spacing: -0.035em;
}

.payment-root .sl-lede.pay-lede {
  margin: 18px auto 0;
  font-size: clamp(16px, 1.5vw, 18.5px);
}

.payment-root .pay-card {
  margin-top: 36px;
  padding: 28px;
  border: 1px solid transparent;
  border-radius: 22px;
  background:
    var(--sl-prompt-bg) padding-box,
    var(--sl-prompt-edge) border-box;
  box-shadow: var(--sl-prompt-shadow);
  color: var(--sl-muted);
  font-size: 16px;
  line-height: 1.6;
}

.payment-root .pay-card--error {
  background:
    var(--sl-prompt-bg) padding-box,
    linear-gradient(140deg, var(--sl-bad), var(--sl-line) 60%) border-box;
}

.payment-root .pay-card__label {
  margin: 22px 0 0;
  padding-top: 22px;
  border-top: 1px solid var(--sl-line);
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-faint);
}

.payment-root .pay-card__value {
  margin: 8px 0 0;
  font-family: var(--sl-font-display);
  font-size: clamp(24px, 3vw, 32px);
  font-weight: 800;
  letter-spacing: -0.025em;
  color: var(--sl-text);
}

.payment-root .pay-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 36px;
}

.payment-root .pay-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto;
  border-radius: 50%;
  border: 3px solid var(--sl-line-strong);
  border-top-color: var(--sl-coral);
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
