<!--
  What Imagi is — the short answer, straight after the hero.
  Who it is for in one line, then the three facts worth knowing before you
  start (free to try, how fast your app is built, who it is made for) on one hairline
  row. The how comes after, in steps 01 to 03.
-->
<template>
  <section id="what-is-imagi" class="sl-sec scroll-mt-14">
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow">What Imagi is</p>
        <h2 class="sl-display sl-h2">For anyone with an idea</h2>
        <p class="sl-lede">
          You don&rsquo;t need to code, hire a developer or stitch a dozen tools together.
          If you can explain it, you can make it.
        </p>
      </div>

      <!-- Three facts between two hairlines: two lit numbers and who it's for -->
      <dl
        v-reveal="{ delay: 60 }"
        class="mx-0 mb-0 mt-[clamp(48px,6vw,72px)] grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_minmax(0,1.3fr)]
          border-y border-y-sl-line max-[900px]:grid-cols-[minmax(0,1fr)]"
      >
        <div
          v-for="(fact, index) in facts"
          :key="fact.label"
          class="flex min-w-0 flex-col items-center gap-3 px-[clamp(16px,2.4vw,32px)] py-[clamp(32px,4vw,44px)] text-center"
          :class="{
            'border-l border-l-sl-line max-[900px]:border-t max-[900px]:border-t-sl-line max-[900px]:[border-left:0]':
              index > 0
          }"
        >
          <dt class="fact__label text-[12px] font-semibold uppercase tracking-[0.18em] text-sl-muted">{{ fact.label }}</dt>
          <!-- m and font-weight are important: .sl-display and .sl-grad-text set them.
               The audience (last) is words, not a number, so it sits smaller on
               the same baseline. -->
          <dd
            class="fact__value sl-display flex min-h-[clamp(56px,6.4vw,84px)] items-end justify-center !m-0 !font-bold
              tabular-nums"
            :class="[
              { 'sl-grad-text': fact.lit },
              index === facts.length - 1
                ? 'text-[length:clamp(22px,2.2vw,28px)] leading-[1.2] tracking-[-0.02em]'
                : 'text-[length:clamp(56px,6.4vw,84px)] leading-none tracking-[-0.045em] drop-shadow-[0_0_30px_var(--sl-text-glow)]'
            ]"
          >
            {{ fact.value }}<span v-if="fact.unit" class="pb-[0.14em] text-[0.45em] tracking-[-0.02em]">&nbsp;{{ fact.unit }}</span>
          </dd>
          <p class="m-0 max-w-[30ch] text-[15px] text-sl-muted text-pretty">{{ fact.caption }}</p>
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
        { label: 'Price', value: 'Free', lit: true, caption: 'Try it in free mode and build your app without paying a thing.' },
        { label: 'Your app is built in under', value: '5', unit: 'sec', lit: true, caption: 'From Create to your home page on screen. The other pages keep building in the background.' },
        { label: 'Made for', value: 'Founders, small businesses and teams', caption: 'And anyone else with an idea worth trying.' }
      ]
    }
  }
})
</script>
