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
          Every business you start on Imagi gets a workspace to build its web app and a
          set of tools to run the business behind it &mdash; not two products stitched together.
        </p>
      </div>

      <!-- The hub itself: four workspaces, one project -->
      <div v-reveal="{ delay: 90 }" class="mt-14 md:mt-16">
        <ProductShot
          src="/product/project-hub.webp"
          alt="The project hub for Ticker Insights, showing its four workspaces: Build, Sell, Market and Operate."
          :width="2200"
          :height="1031"
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
          <HomeCardIcon :name="metric.icon" class="rule-col__icon" />
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
import { HomeCardIcon, ProductShot } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'StatsSection',
  components: { HomeCardIcon, ProductShot },
  directives: { reveal },
  props: {
    stats: {
      type: Array,
      default: () => [
        {
          value: 'Free',
          unit: '',
          label: 'Plans start at',
          caption: 'Usage refreshes on a rolling 5-hour session and a weekly limit. Upgrade as you grow, cancel anytime.'
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
