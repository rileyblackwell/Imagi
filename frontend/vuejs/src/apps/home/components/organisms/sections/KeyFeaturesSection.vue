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
          <LineIcon :name="feature.icon" class="rule-col__icon" />
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

<!-- Layout comes entirely from .rule-cols / .checklist in
     shared/styles/editorial.css -->

<style scoped>
/* Stacked, not side by side: these crops are 1800px of dense UI, and at half
   the measure their tab labels stop being readable — which defeats the point
   of showing them at all. */
.shot-pair {
  display: grid;
  grid-template-columns: 1fr;
  gap: 3rem;
}
</style>
