<!--
  Step 02 — Build.
  Three cards explaining the workspace, then a screenshot of the real thing,
  lit on stage. The shot lives here rather than in the hero because this is
  the section that describes what it shows.
-->
<template>
  <section class="sl-sec step">
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow"><span class="sl-grad-text step-num">02</span><span>Build</span></p>
        <h2 class="sl-display sl-h2">Build your web app</h2>
        <p class="sl-lede">
          Tell Imagi what you want and it goes to work. You watch the app take shape and
          step in only when a choice is yours to make.
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

      <!-- The workspace itself, illustrating the three cards above it -->
      <div v-reveal="{ delay: 120 }" class="sl-stage">
        <ProductShot
          src="/product/build-workspace.webp"
          alt="The Imagi build workspace: the coordinator has split a request into two threads, one finished and one still working, and on the right the live stock-tracking app it wrote, with a watchlist snapshot of AAPL, TSLA and MSFT prices."
          :width="2400"
          :height="1500"
          label="imagi — build workspace"
          caption="A real project mid-conversation: “Ticker Insights”, a stock tracker with AI-written summaries, built from a description and running live beside the chat."
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
  name: 'FeaturesSection',
  components: { LineIcon, ProductShot },
  directives: { reveal },
  props: {
    features: {
      type: Array,
      default: () => [
        {
          title: 'Just say what you want',
          description: 'Ask for a page, a feature or a fix in plain words. The coordinator turns it into a plan and checks with you when something is yours to decide.',
          icon: 'chat',
          highlights: ['Plain-language requests', 'Questions you answer in a tap', 'Real Vue and Django code']
        },
        {
          title: 'Threads do the work',
          description: 'The coordinator hands the work to threads that build side by side. They keep going if you close the tab, and fixes go back to the thread that caused them.',
          icon: 'teams',
          highlights: ['Pages built in parallel', 'Fixes its own errors', 'Keeps working while you’re away']
        },
        {
          title: 'A live app beside you',
          description: 'Your app runs next to the chat the whole time. The agent uses it like a person would, clicking and typing to check its own work, and so can you.',
          icon: 'design',
          highlights: ['Live preview', 'The agent drives your app', 'Changes land as they’re made']
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
