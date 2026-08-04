<!--
  Step 01 — Build.

  Three ruled columns explaining the workspace, then a screenshot of the real
  thing. The shot lives here rather than in the hero because this is the
  section that describes what it shows.
-->
<template>
  <section class="relative py-20 md:py-28">
    <div class="section-shell">
      <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>

      <div v-reveal class="md:flex md:items-end md:justify-between gap-14">
        <div class="max-w-xl">
          <p class="eyebrow">
            <span class="eyebrow__num">01</span>
            <span class="eyebrow__rule" aria-hidden="true"></span>
            <span>Build</span>
          </p>
          <h2 class="display mt-6 text-4xl sm:text-5xl md:text-[3.2rem]">
            Build your web app
          </h2>
        </div>
        <p class="lede mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg">
          Every business starts with a product. Chat with the agent, watch the app take
          shape in the preview beside you, and put it online when it's ready.
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

      <!-- The workspace itself, illustrating the three columns above it -->
      <div v-reveal="{ delay: 120 }" class="mt-16 md:mt-20">
        <ProductShot
          src="/product/build-workspace.webp"
          alt="The Imagi build workspace: a conversation with the agent on the left, and on the right the live stock-tracking app it wrote — a portfolio snapshot with AAPL and TSLA prices and AI-written summaries."
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
import { HomeCardIcon, ProductShot } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'FeaturesSection',
  components: { HomeCardIcon, ProductShot },
  directives: { reveal },
  props: {
    features: {
      type: Array,
      default: () => [
        {
          title: 'Design visually',
          description: 'Shape the application without touching a file. Changes land in the preview as you make them.',
          icon: 'design',
          highlights: ['Visual builder', 'Live preview', 'Component library']
        },
        {
          title: 'Chat and plan',
          description: 'An agent that understands the business you are describing, not just the code. Plan features, work through problems, and write it together.',
          icon: 'chat',
          highlights: ['Plain-language briefs', 'Real Vue and Django code', 'Iterate by conversation']
        },
        {
          title: 'Launch to the web',
          description: 'Deploy in a click and get a URL you can send to real customers the same afternoon.',
          icon: 'launch',
          highlights: ['One-click deploy', 'Custom domains', 'Instant updates']
        }
      ]
    }
  }
})
</script>

<!-- Layout comes entirely from .rule-cols / .checklist in
     shared/styles/editorial.css -->
