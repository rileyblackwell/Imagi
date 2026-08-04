<!--
  Step 01 — Build.

  Three ruled columns, each with a short checklist. Deliberately quiet: the hero
  already showed the workspace, so this section explains it rather than
  re-illustrating it.
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
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import { HomeCardIcon } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'FeaturesSection',
  components: { HomeCardIcon },
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
</style>
