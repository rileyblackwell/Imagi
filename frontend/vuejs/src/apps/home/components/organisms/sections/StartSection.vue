<!--
  Step 01 — Create.
  The first thing anyone does on Imagi: create a project. The real create
  form's three numbered steps are named (the app's name sits above them, so
  it is not one), then shown on stage: the steps on their rail beside the
  pinned preview of the app, then the starter-design step's style tiles.
-->
<template>
  <section
    id="how-it-works"
    class="sl-sec scroll-mt-14 isolate overflow-hidden
      before:pointer-events-none before:absolute before:left-1/2 before:top-0 before:z-[-1] before:h-[560px]
      before:w-[min(1100px,140vw)] before:-translate-x-1/2 before:content-['']
      before:bg-[radial-gradient(ellipse_50%_60%_at_50%_0%,var(--sl-section-glow),transparent_70%)]"
  >
    <!-- A softer pool of light at the top of the step, as on steps 02 and 03 -->
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow"><span class="sl-grad-text font-bold">01</span><span>Create</span></p>
        <h2 class="sl-display sl-h2">Create a project</h2>
        <p class="sl-lede">
          Every app on Imagi starts as a project. Name your app, answer three questions in your
          own words, and the first version starts building the moment you create it.
        </p>
      </div>

      <!-- The form's three steps, in a row on a hairline, numbered like the form -->
      <ol
        v-reveal="{ delay: 60 }"
        class="mx-0 mb-0 mt-[clamp(48px,6vw,72px)] grid list-none grid-cols-3 gap-0 border-t border-t-sl-line p-0
          max-[560px]:grid-cols-1 max-[560px]:gap-y-6"
      >
        <li
          v-for="(item, index) in steps"
          :key="item.title"
          class="flex min-w-0 flex-col gap-2 pb-0 pr-[clamp(16px,2vw,28px)] pt-6"
          :class="index > 0
            ? 'border-l border-l-sl-line pl-[clamp(16px,2vw,28px)] max-[560px]:pl-0 max-[560px]:[border-left:0]'
            : 'pl-0'"
        >
          <span class="text-[12px] font-semibold tracking-[0.18em] text-sl-muted tabular-nums">{{ String(index + 1).padStart(2, '0') }}</span>
          <h3 class="brief-step__title m-0 text-[18px] font-semibold tracking-[-0.01em]">{{ item.title }}</h3>
          <p class="m-0 text-[15px] text-sl-muted text-pretty">{{ item.body }}</p>
        </li>
      </ol>

      <!-- The create form itself, filled in for Ticker Insights -->
      <!-- The form shot: held to the homepage's 920px, so the words lead -->
      <div v-reveal="{ delay: 120 }" class="sl-stage mx-auto max-w-[920px]">
        <ProductShot
          src="/product/create-brief.webp"
          alt="The Imagi create form for Ticker Insights: the app's name as the headline, its steps checked off on a lit rail, and a live preview of the app beside them with the Create app button."
          :width="2312"
          :height="1718"
          label="imagi — new project"
          caption="Each step lights up once it has enough to build from, and the preview follows what you type. Then choose Create app."
        />
      </div>

      <!-- Set the look: the words on one side, its screenshot on the other -->
      <div
        v-reveal="{ delay: 120 }"
        class="mt-[clamp(64px,8vw,104px)] grid grid-cols-[minmax(0,5fr)_minmax(0,7fr)] items-center
          gap-[clamp(32px,5vw,72px)] max-[900px]:grid-cols-[minmax(0,1fr)]"
      >
        <div>
          <!-- font-weight is important: .sl-display sets 800 -->
          <h3 class="sl-display text-[length:clamp(26px,2.6vw,34px)] !font-bold leading-[1.1] tracking-[-0.03em]">
            See the look before it&rsquo;s built
          </h3>
          <p class="mx-0 mb-0 mt-4 max-w-[40ch] text-sl-muted">
            Pick a style and a colour scheme and watch your app take shape, with its own name,
            before the first build starts. Skip it and Imagi picks a look that fits.
          </p>
        </div>
        <!-- mt is important: .sl-stage sets its own -->
        <div class="sl-stage !mt-0">
          <ProductShot
            src="/product/create-look.webp"
            alt="The Set the look step: style tiles showing Ticker Insights in each style, and a row of colour schemes."
            :width="1124"
            :height="1466"
            label="imagi — set the look"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import { ProductShot } from '@/apps/home/components/atoms'

export default defineComponent({
  name: 'StartSection',
  components: { ProductShot },
  directives: { reveal },
  props: {
    steps: {
      type: Array,
      default: () => [
        { title: 'What is your app?', body: 'A few sentences on what it is, who it’s for, and what it should help them do.' },
        { title: 'How does it work?', body: 'What people can do on it and what it keeps track of. Imagi turns this into the plan.' },
        { title: 'Set the look', body: 'Optional. A starter design, previewed on your app’s own name.' }
      ]
    }
  }
})
</script>
