<!--
  Step 03 — Run.
  The mirror of step 02, plus one real crop of the run-half tooling so the
  claim that these are actual workspaces (and not a roadmap) is visible rather
  than asserted. Sell, Market and Operate are in beta, and say so.
-->
<template>
  <section class="sl-sec step">
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow"><span class="sl-grad-text step-num">03</span><span>Run</span><StatusBadge tone="neutral" label="Beta" /></p>
        <h2 class="sl-display sl-h2">Run it as a business</h2>
        <p class="sl-lede">
          When the app is ready for customers, the business tools are already in the project.
          All three are in beta: they work today and are still growing.
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

      <!-- One crop of the real tooling: starting a campaign -->
      <div v-reveal="{ delay: 120 }" class="sl-stage">
        <ProductShot
          src="/product/run-marketing.webp"
          alt="The Marketing workspace for Ticker Insights, with two ways to start a campaign: a text message sent through Twilio, or a Google search ad."
          :width="2288"
          :height="1194"
          label="imagi — marketing"
          caption="Texts go out over your Twilio account and replies land in your inbox. Google search ads can be planned now and launched once Google Ads is connected."
        />
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import { ProductShot } from '@/apps/home/components/atoms'
import { LineIcon, StatusBadge } from '@/shared/components'

export default defineComponent({
  name: 'KeyFeaturesSection',
  components: { LineIcon, ProductShot, StatusBadge },
  directives: { reveal },
  props: {
    features: {
      type: Array,
      default: () => [
        {
          title: 'Marketing',
          description: 'Reach customers and grow an audience: text campaigns to your contacts, Google search ads, and an inbox for the replies.',
          icon: 'marketing',
          highlights: ['Text campaigns', 'Google search ads', 'Contacts and inbox']
        },
        {
          title: 'Sell',
          description: 'Turn visitors into paying customers. Connect Stripe, choose how you charge, and Imagi adds secure payment pages to the app you just built.',
          icon: 'sales',
          highlights: ['One-time, subscription or pay as you go', 'Orders, subscriptions and customers', 'Paid through your Stripe']
        },
        {
          title: 'Operate',
          description: 'One dashboard for running it: whether your app is up and fast, who is visiting, and what the business is making.',
          icon: 'finance',
          highlights: ['Uptime and response time', 'Visitors to your app', 'Revenue, expenses and profit']
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

</style>
