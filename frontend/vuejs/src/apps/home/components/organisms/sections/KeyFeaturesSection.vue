<!--
  Step 02 — Run.
  The mirror of step 01, plus two real crops of the run-half tooling so the
  claim that these are actual workspaces (and not a roadmap) is visible rather
  than asserted.
-->
<template>
  <section class="sl-sec step">
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow"><span class="sl-grad-text step-num">02</span><span>Run</span></p>
        <h2 class="sl-display sl-h2">Run the business</h2>
        <p class="sl-lede">
          Once the app is live, the rest of the business lives in the same project &mdash;
          reaching customers, taking payments, and keeping track of the money.
        </p>
      </div>

      <div class="sl-cards">
        <article
          v-for="(feature, index) in features"
          :key="feature.title"
          v-reveal="{ delay: 80 + index * 80 }"
          class="sl-card"
        >
          <span class="sl-card__icon"><LineIcon :name="feature.icon" /></span>
          <h3 class="sl-card__title">{{ feature.title }}</h3>
          <p class="sl-card__body">{{ feature.description }}</p>
          <ul class="sl-highlights">
            <li v-for="highlight in feature.highlights" :key="highlight">{{ highlight }}</li>
          </ul>
        </article>
      </div>

      <!-- Two crops of the real tooling: payments and campaigns -->
      <div v-reveal="{ delay: 120 }" class="shot-pair">
        <div class="sl-stage">
          <ProductShot
            src="/product/run-sell.webp"
            alt="The Sell workspace for Ticker Insights, with tabs for payments, products, orders, customers and settings, and a prompt to connect a Stripe account."
            :width="1800"
            :height="414"
            label="imagi — sell"
            caption="Payments run through your own Stripe account — Imagi never sits between you and the money."
          />
        </div>
        <div class="sl-stage">
          <ProductShot
            src="/product/run-marketing.webp"
            alt="The Marketing workspace for Ticker Insights, with tabs for campaigns, audience, ads, inbox and settings, and a prompt to connect a Twilio account."
            :width="1800"
            :height="420"
            label="imagi — marketing"
            caption="Text and voice campaigns go out over Twilio, with Google and Meta ad accounts alongside them."
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import { ProductShot } from '@/apps/home/components/atoms'
import { LineIcon } from '@/shared/components'

export default defineComponent({
  name: 'KeyFeaturesSection',
  components: { LineIcon, ProductShot },
  directives: { reveal },
  props: {
    features: {
      type: Array,
      default: () => [
        {
          title: 'Marketing',
          description: 'Reach customers and grow an audience — campaigns, contacts, ad accounts and a shared inbox for the replies.',
          icon: 'marketing',
          highlights: ['Text and voice campaigns', 'Google and Meta ads', 'Contacts and inbox']
        },
        {
          title: 'Sell',
          description: 'Turn visitors into paying customers with products, checkout links and orders wired into the app you just built.',
          icon: 'sales',
          highlights: ['Products and checkout links', 'Orders and customers', 'Paid through your Stripe']
        },
        {
          title: 'Operate',
          description: 'Stay on top of the numbers — invoices out, income and expenses tracked, and the work that keeps it running.',
          icon: 'finance',
          highlights: ['Invoicing and billing', 'Income and expenses', 'Operational tasks']
        }
      ]
    }
  }
})
</script>

<style scoped>
/* A softer pool of light at the top of each step */
.step {
  isolation: isolate;
  overflow: hidden;
}

.step::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  z-index: -1;
  width: min(1100px, 140vw);
  height: 560px;
  transform: translateX(-50%);
  pointer-events: none;
  background: radial-gradient(ellipse 50% 60% at 50% 0%, var(--sl-section-glow), transparent 70%);
}

.step-num {
  font-weight: 700;
}

/* Stacked, not side by side: these crops are 1800px of dense UI, and at half
   the measure their tab labels stop being readable — which defeats the point
   of showing them at all. */
.shot-pair {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: clamp(40px, 5vw, 64px);
  margin-top: clamp(64px, 8vw, 104px);
}

.shot-pair .sl-stage {
  margin-top: 0;
}
</style>
