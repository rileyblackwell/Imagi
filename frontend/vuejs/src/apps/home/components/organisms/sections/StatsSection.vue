<!--
  "Why Imagi" — the shape of the product, shown rather than asserted.

  This is where the two-halves idea lands: a screenshot of the real project hub
  (Build / Sell / Market / Operate), a spec row of the few numbers we can state
  honestly, and the audiences as hairline-ruled columns instead of cards.
-->
<template>
  <section id="why-imagi" class="relative py-20 md:py-28 scroll-mt-14">
    <div class="section-shell">
      <div class="section-rule mb-14 md:mb-16" aria-hidden="true"></div>

      <!-- Header: headline left, supporting copy right -->
      <div v-reveal class="md:flex md:items-end md:justify-between gap-14">
        <div class="max-w-xl">
          <p class="eyebrow">
            <span class="eyebrow__rule" aria-hidden="true"></span>
            <span>Why Imagi</span>
          </p>
          <h2 class="display mt-6 text-4xl sm:text-5xl md:text-[3.2rem]">
            One project. Two halves.
          </h2>
        </div>
        <p class="lede mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg">
          Every business on Imagi is one project with two sets of tools: one for building
          its web app, and one for running the business once the app is live.
        </p>
      </div>

      <!-- The two halves, spelled out -->
      <div v-reveal="{ delay: 60 }" class="rule-cols rule-cols--2 mt-14 md:mt-16">
        <div v-for="half in halves" :key="half.name" class="rule-col">
          <p class="half__name">
            <span class="half__mark" aria-hidden="true"></span>{{ half.name }}
          </p>
          <h3 class="half__title display">{{ half.title }}</h3>
          <p class="rule-col__body">{{ half.body }}</p>
          <ul class="half__tools">
            <li v-for="tool in half.tools" :key="tool">{{ tool }}</li>
          </ul>
        </div>
      </div>

      <p v-reveal="{ delay: 90 }" class="half__join">
        Both halves live in the same project, so the business and its app are never
        in two places.
      </p>

      <!-- The hub itself: four workspaces, one project -->
      <div v-reveal="{ delay: 90 }" class="mt-14 md:mt-16">
        <ProductShot
          src="/product/project-hub.webp"
          alt="The project hub for Ticker Insights, showing its four workspaces: Build, Sell, Market and Operate."
          :width="2400"
          :height="1752"
          label="imagi — project hub"
          caption="The hub for Ticker Insights. Build makes the product; Sell, Market and Operate run the business around it."
        />
      </div>

      <!-- Spec row: only numbers we can actually stand behind -->
      <dl v-reveal="{ delay: 120 }" class="spec-row mt-16 md:mt-20">
        <div v-for="stat in stats" :key="stat.label" class="spec">
          <dt class="spec__label">{{ stat.label }}</dt>
          <dd class="spec__value display">
            {{ stat.value }}<span v-if="stat.unit" class="spec__unit">{{ stat.unit }}</span>
          </dd>
          <p class="spec__caption">{{ stat.caption }}</p>
        </div>
      </dl>

      <!-- Audiences -->
      <div v-reveal="{ delay: 150 }" class="rule-cols mt-16 md:mt-20">
        <div v-for="metric in metrics" :key="metric.title" class="rule-col">
          <LineIcon :name="metric.icon" class="rule-col__icon" />
          <h3 class="rule-col__title">{{ metric.title }}</h3>
          <p class="rule-col__body">{{ metric.description }}</p>
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
  name: 'StatsSection',
  components: { LineIcon, ProductShot },
  directives: { reveal },
  props: {
    halves: {
      type: Array,
      default: () => [
        {
          name: 'Build',
          title: 'Tools to build the app',
          body: 'Describe the business and an AI agent writes a real web app for it. You watch it take shape in a live preview, change it by chatting, and put it online in a click.',
          tools: ['AI agent', 'Live preview', 'Real Vue and Django code', 'One-click deploy']
        },
        {
          name: 'Run',
          title: 'Tools to run the business',
          body: 'Once the app is live, the same project carries everything around it: taking payments, finding and talking to customers, and keeping the money and the work in order.',
          tools: ['Sell: products, checkout, orders', 'Market: campaigns, contacts, inbox', 'Operate: invoices, books, tasks']
        }
      ]
    },
    stats: {
      type: Array,
      default: () => [
        {
          value: 'Free',
          unit: '',
          label: 'Plans start at',
          caption: 'Usage refreshes on a rolling weekly limit. Upgrade as you grow, cancel anytime.'
        },
        {
          value: '30',
          unit: 'min',
          label: 'Typical build',
          caption: 'From the first prompt to a working app you can open and share.'
        },
        {
          value: '4',
          unit: '',
          label: 'Workspaces per project',
          caption: 'Build, Sell, Market and Operate — all pointed at the same business.'
        }
      ]
    },
    metrics: {
      type: Array,
      default: () => [
        {
          icon: 'founders',
          title: 'Founders',
          description: 'Go from idea to a running business without a technical co-founder. Build the app, then find customers and grow revenue in the same place.'
        },
        {
          icon: 'business',
          title: 'Small businesses',
          description: 'Get online and keep marketing, sales and finances together, instead of stitching a dozen separate subscriptions into something that half works.'
        },
        {
          icon: 'teams',
          title: 'Teams',
          description: 'Ship products and run operations without queueing behind engineering for every change to the website.'
        }
      ]
    }
  }
})
</script>

<style scoped>
.half__name {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--ink-55);
}

.half__mark {
  width: 0.3rem;
  height: 0.3rem;
  transform: rotate(45deg);
  background: var(--accent);
}

.half__title {
  margin-top: 0.9rem;
  font-size: 1.75rem;
}

.half__tools {
  margin: auto 0 0;
  padding: 1.1rem 0 0;
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  border-top: 1px solid var(--rule);
}

.half__tools li {
  font-size: 0.8rem;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  border: 1px solid var(--rule);
  color: var(--ink-70);
}

.half__join {
  margin-top: 2.5rem;
  font-family: var(--font-display);
  font-style: italic;
  font-size: 1.2rem;
  color: var(--ink-70);
  text-wrap: balance;
}

/* Only the spec row is local — the ruled columns below it come from
   .rule-cols in shared/styles/editorial.css. */
.spec-row {
  display: grid;
  grid-template-columns: 1fr;
  border-top: 1px solid var(--rule);
}

.spec {
  padding: 2rem 0;
  border-bottom: 1px solid var(--rule);
}

@media (min-width: 768px) {
  .spec-row {
    grid-template-columns: repeat(3, 1fr);
    border-bottom: 1px solid var(--rule);
  }

  .spec {
    padding: 2.25rem 2rem 2.25rem 0;
    border-bottom: 0;
  }

  .spec + .spec {
    padding-left: 2rem;
    border-left: 1px solid var(--rule);
  }
}

.spec__label {
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--ink-40);
}

.spec__value {
  margin: 0.75rem 0 0;
  font-size: 3rem;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.spec__unit {
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--ink-40);
  margin-left: 0.3rem;
}

.spec__caption {
  margin-top: 0.9rem;
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--ink-55);
  text-wrap: pretty;
}
</style>
