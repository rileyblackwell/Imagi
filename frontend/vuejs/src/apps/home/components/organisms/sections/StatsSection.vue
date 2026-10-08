<!--
  "Why Imagi" — the shape of the product, shown rather than asserted.
  This is where the two-halves idea lands: Build and Run as two lit panels
  (Build cool, Run warm), the real project hub on stage, a row of the few
  numbers we can state honestly, and the audiences as cards.
-->
<template>
  <section id="why-imagi" class="sl-sec scroll-mt-14">
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow">Why Imagi</p>
        <h2 class="sl-display sl-h2">One project. Two halves.</h2>
        <p class="sl-lede">
          Every business on Imagi is one project with two sets of tools: one for building
          its web app, and one for running the business once the app is live.
        </p>
      </div>

      <!-- The two halves, spelled out -->
      <div v-reveal="{ delay: 60 }" class="halves">
        <article
          v-for="half in halves"
          :key="half.name"
          class="half"
          :class="half.name === 'Build' ? 'half--build' : 'half--run'"
        >
          <div class="half__label">
            <span class="half__badge">
              <svg v-if="half.name === 'Build'" viewBox="0 0 24 24" aria-hidden="true"><path d="m8 7-5 5 5 5M16 7l5 5-5 5M14 4l-4 16" /></svg>
              <svg v-else viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17l5-5 4 4 8-8" /><path d="M15 8h5v5" /></svg>
            </span>
            <span class="half__name">{{ half.name }}</span>
          </div>
          <h3 class="half__title sl-display">{{ half.title }}</h3>
          <p class="half__body">{{ half.body }}</p>
          <ul class="half__tools">
            <li v-for="tool in half.tools" :key="tool">{{ tool }}</li>
          </ul>
        </article>
      </div>

      <p v-reveal="{ delay: 90 }" class="half__join sl-display">
        Both halves live in the same project, so the business and its app are never
        in two places.
      </p>

      <!-- The hub itself: four workspaces, one project -->
      <div v-reveal="{ delay: 90 }" class="sl-stage">
        <ProductShot
          src="/product/project-hub.webp"
          alt="The project hub for Ticker Insights, showing its four workspaces: Build, Sell, Market and Operate."
          :width="2560"
          :height="1702"
          label="imagi — project hub"
          caption="The hub for Ticker Insights. Build makes the product; Sell, Market and Operate run the business around it."
        />
      </div>

      <!-- Spec row: only numbers we can actually stand behind -->
      <dl v-reveal="{ delay: 120 }" class="spec-row">
        <div v-for="stat in stats" :key="stat.label" class="spec">
          <dt class="spec__label">{{ stat.label }}</dt>
          <dd class="spec__value sl-display sl-grad-text">
            {{ stat.value }}<span v-if="stat.unit" class="spec__unit">&nbsp;{{ stat.unit }}</span>
          </dd>
          <p class="spec__caption">{{ stat.caption }}</p>
        </div>
      </dl>

      <!-- Audiences -->
      <div v-reveal="{ delay: 150 }" class="sl-cards audiences">
        <article v-for="metric in metrics" :key="metric.title" class="sl-card">
          <span class="sl-card__icon"><LineIcon :name="metric.icon" /></span>
          <h3 class="sl-card__title">{{ metric.title }}</h3>
          <p class="sl-card__body">{{ metric.description }}</p>
        </article>
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
          tools: ['Sell: products, checkout, orders', 'Market: campaigns, contacts, inbox', 'Operate: uptime, visitors, profit']
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
.halves {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  margin-top: clamp(48px, 6vw, 72px);
}

.half {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
  padding: clamp(26px, 3.4vw, 40px);
  overflow: hidden;
  border-radius: 20px;
  border: 1px solid var(--sl-line);
  box-shadow: var(--sl-card-shadow);
}

/* Build is lit cool from the left, Run warm from the right */
.half--build {
  border-color: var(--sl-cool-line);
  background: var(--sl-half-build-bg);
  --half-ink: var(--sl-cool);
}

.half--run {
  border-color: var(--sl-warm-line);
  background: var(--sl-half-run-bg);
  --half-ink: var(--sl-focus);
}

.half__label {
  display: flex;
  align-items: center;
  gap: 12px;
}

.half__badge {
  display: grid;
  place-items: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid var(--sl-line-strong);
  background: var(--sl-chip-bg);
}

.half__badge svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: var(--half-ink);
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.half__name {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--half-ink);
}

.half .half__title {
  margin-top: 8px;
  font-size: clamp(26px, 2.6vw, 34px);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.half__body {
  margin: 0;
  max-width: 46ch;
  color: var(--sl-muted);
}

.half__tools {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.half__tools li {
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--sl-line);
  background: var(--sl-chip-bg);
  font-size: 13.5px;
  font-weight: 500;
}

/* The join: a short beam of light falling onto one line */
.sl-wrap .half__join {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
  max-width: 34ch;
  margin: 44px auto 0;
  text-align: center;
  font-size: clamp(18px, 1.8vw, 22px);
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: -0.01em;
}

.half__join::before {
  content: '';
  width: 1px;
  height: 40px;
  background: linear-gradient(180deg, transparent, var(--sl-amber));
}

.spec-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: clamp(72px, 9vw, 120px) 0 0;
  border-top: 1px solid var(--sl-line);
  border-bottom: 1px solid var(--sl-line);
}

.spec {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  min-width: 0;
  padding: 40px clamp(20px, 3vw, 40px);
  text-align: center;
}

.spec + .spec {
  border-left: 1px solid var(--sl-line);
}

.spec__label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.spec .spec__value {
  margin: 0;
  padding-block: 6px;
  font-size: clamp(64px, 7.6vw, 104px);
  line-height: 1;
  letter-spacing: -0.05em;
  font-variant-numeric: tabular-nums;
  filter: drop-shadow(0 0 30px var(--sl-text-glow));
}

.spec__caption {
  margin: 0;
  max-width: 30ch;
  font-size: 15px;
  color: var(--sl-muted);
  text-wrap: pretty;
}

.audiences {
  margin-top: clamp(56px, 7vw, 88px);
}

@media (max-width: 900px) {
  .halves,
  .spec-row {
    grid-template-columns: minmax(0, 1fr);
  }

  .spec + .spec {
    border-left: 0;
    border-top: 1px solid var(--sl-line);
  }
}
</style>
