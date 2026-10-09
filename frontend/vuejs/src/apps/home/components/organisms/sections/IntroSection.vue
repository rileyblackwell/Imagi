<!--
  What Imagi is — the short answer, straight after the hero.
  Who it is for in one line, then the three facts worth knowing before you
  start (free to start, a typical build, who it is made for) on one hairline
  row. The how comes after, in steps 01 to 03.
-->
<template>
  <section id="what-is-imagi" class="sl-sec scroll-mt-14">
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow">What Imagi is</p>
        <h2 class="sl-display sl-h2">For anyone with an idea</h2>
        <p class="sl-lede">
          No code, no developer, no stack of separate subscriptions. If you can explain your
          idea, you can build it on Imagi and run it there too.
        </p>
      </div>

      <dl v-reveal="{ delay: 60 }" class="facts">
        <div v-for="fact in facts" :key="fact.label" class="fact">
          <dt class="fact__label">{{ fact.label }}</dt>
          <dd class="fact__value sl-display" :class="{ 'sl-grad-text': fact.lit }">
            {{ fact.value }}<span v-if="fact.unit" class="fact__unit">&nbsp;{{ fact.unit }}</span>
          </dd>
          <p class="fact__caption">{{ fact.caption }}</p>
        </div>
      </dl>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'

export default defineComponent({
  name: 'IntroSection',
  directives: { reveal },
  props: {
    facts: {
      type: Array,
      default: () => [
        { label: 'Plans start at', value: 'Free', lit: true, caption: 'Upgrade as you grow, cancel anytime.' },
        { label: 'Typical build', value: '10', unit: 'min', lit: true, caption: 'From your brief to an app you can open and share.' },
        { label: 'Made for', value: 'Founders, small businesses and teams', caption: 'No technical co-founder or engineering queue needed.' }
      ]
    }
  }
})
</script>

<style scoped>
/* Three facts between two hairlines: two lit numbers and who it's for */
.facts {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.3fr);
  margin: clamp(48px, 6vw, 72px) 0 0;
  border-top: 1px solid var(--sl-line);
  border-bottom: 1px solid var(--sl-line);
}

.fact {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: clamp(32px, 4vw, 44px) clamp(16px, 2.4vw, 32px);
  text-align: center;
}

.fact + .fact {
  border-left: 1px solid var(--sl-line);
}

.fact__label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.fact .fact__value {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  min-height: clamp(56px, 6.4vw, 84px);
  margin: 0;
  font-size: clamp(56px, 6.4vw, 84px);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.045em;
  font-variant-numeric: tabular-nums;
  filter: drop-shadow(0 0 30px var(--sl-text-glow));
}

.fact__unit {
  font-size: 0.45em;
  letter-spacing: -0.02em;
  padding-bottom: 0.14em;
}

/* The audience is words, not a number, so it sits smaller on the same baseline */
.fact:last-child .fact__value {
  font-size: clamp(22px, 2.2vw, 28px);
  line-height: 1.2;
  letter-spacing: -0.02em;
  text-wrap: balance;
  filter: none;
}

.fact__caption {
  margin: 0;
  max-width: 30ch;
  font-size: 15px;
  color: var(--sl-muted);
  text-wrap: pretty;
}

@media (max-width: 900px) {
  .facts {
    grid-template-columns: minmax(0, 1fr);
  }

  .fact + .fact {
    border-left: 0;
    border-top: 1px solid var(--sl-line);
  }
}
</style>
