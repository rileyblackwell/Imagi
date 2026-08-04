<!--
  Step 02 — Run.

  The mirror of step 01, plus two real crops of the run-half tooling so the
  claim that these are actual workspaces (and not a roadmap) is visible rather
  than asserted.
-->
<template>
  <section class="relative py-20 md:py-28">
    <div class="section-shell">
      <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>

      <div v-reveal class="md:flex md:items-end md:justify-between gap-14">
        <div class="max-w-xl">
          <p class="eyebrow">
            <span class="eyebrow__num">02</span>
            <span class="eyebrow__rule" aria-hidden="true"></span>
            <span>Run</span>
          </p>
          <h2 class="display mt-6 text-4xl sm:text-5xl md:text-[3.2rem]">
            Run the business
          </h2>
        </div>
        <p class="lede mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg">
          Once the app is live, the rest of the business lives in the same project &mdash;
          reaching customers, taking payments, and keeping track of the money.
        </p>
      </div>

      <div class="rule-cols mt-14 md:mt-16">
        <div
          v-for="(feature, index) in features"
          :key="feature.title"
          v-reveal="{ delay: 80 + index * 80 }"
          class="rule-col"
        >
          <HomeCardIcon :name="feature.icon" class="rule-col__icon" />
          <h3 class="rule-col__title">{{ feature.title }}</h3>
          <p class="rule-col__body">{{ feature.description }}</p>

          <ul class="checklist">
            <li v-for="highlight in feature.highlights" :key="highlight">
              <span class="checklist__tick" aria-hidden="true"></span>
              <span>{{ highlight }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Two crops of the real tooling: payments and campaigns -->
      <div v-reveal="{ delay: 120 }" class="shot-pair mt-16 md:mt-20">
        <ProductShot
          src="/product/run-sell.webp"
          alt="The Sell workspace for Ticker Insights, with tabs for payments, products, orders, customers and settings, and a prompt to connect a Stripe account."
          :width="1800"
          :height="420"
          label="imagi — sell"
          caption="Payments run through your own Stripe account — Imagi never sits between you and the money."
        />
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
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import { HomeCardIcon, ProductShot } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'KeyFeaturesSection',
  components: { HomeCardIcon, ProductShot },
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
.rule-cols {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2.75rem;
}

/* Columns stretch to a common height and the checklist is pushed to the
   bottom, so the hairline above it lands on the same baseline in all three
   regardless of how long each description runs. */
.rule-col {
  display: flex;
  flex-direction: column;
}

.rule-col .checklist {
  margin-top: auto;
}

@media (min-width: 768px) {
  .rule-cols {
    grid-template-columns: repeat(3, 1fr);
    gap: 0;
    align-items: stretch;
  }

  .rule-col {
    padding: 0 2rem 0 0;
  }

  .rule-col + .rule-col {
    padding-left: 2rem;
    border-left: 1px solid var(--rule);
  }
}

/* Size comes from HomeCardIcon's own scoped rule — only the ink is ours. */
.rule-col__icon {
  color: var(--accent);
}

.rule-col__title {
  margin-top: 1.1rem;
  font-size: 1.0625rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--ink);
}

.rule-col__body {
  margin-top: 0.65rem;
  /* Floor for the gap the checklist's `margin-top: auto` would otherwise
     collapse to in the tallest column. */
  margin-bottom: 1.4rem;
  font-size: 0.9375rem;
  line-height: 1.65;
  color: var(--ink-55);
  text-wrap: pretty;
}

.checklist {
  padding-top: 1.25rem;
  border-top: 1px solid var(--rule);
  display: grid;
  gap: 0.65rem;
}

.checklist li {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--ink-70);
}

.checklist__tick {
  flex: none;
  width: 0.3rem;
  height: 0.3rem;
  border-radius: 999px;
  background: var(--accent);
  transform: translateY(-0.15em);
}

/* Stacked, not side by side: these crops are 1800px of dense UI, and at half
   the measure their tab labels stop being readable — which defeats the point
   of showing them at all. */
.shot-pair {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
}
</style>
