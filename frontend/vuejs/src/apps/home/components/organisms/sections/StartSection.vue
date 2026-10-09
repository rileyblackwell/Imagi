<!--
  Step 01 — Start.
  The first thing anyone does on Imagi: brief the agent on a new app. The
  four steps of the real create form are named here, then shown on stage: the
  brief with the card that sums it up, and the starter-design step with its
  live preview of the app's own name.
-->
<template>
  <section id="how-it-works" class="sl-sec step scroll-mt-14">
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow"><span class="sl-grad-text step-num">01</span><span>Start</span></p>
        <h2 class="sl-display sl-h2">Start with a brief</h2>
        <p class="sl-lede">
          Answer four questions in your own words. Imagi turns them into the brief its
          agent builds from, and your first version starts building the moment you
          create the project.
        </p>
      </div>

      <ol v-reveal="{ delay: 60 }" class="brief-steps">
        <li v-for="(item, index) in steps" :key="item.title" class="brief-step">
          <span class="brief-step__num">{{ String(index + 1).padStart(2, '0') }}</span>
          <h3 class="brief-step__title">{{ item.title }}</h3>
          <p class="brief-step__body">{{ item.body }}</p>
        </li>
      </ol>

      <!-- The create form itself, filled in for Ticker Insights -->
      <div v-reveal="{ delay: 120 }" class="sl-stage">
        <ProductShot
          src="/product/create-brief.webp"
          alt="The Imagi create form for Ticker Insights: the app's name, what it is and how it works filled in, and beside them the card showing what the agent receives, with a Create project button."
          :width="2400"
          :height="1550"
          label="imagi — new project"
          caption="Each answer fills in the card on the right, so you see exactly what the agent will get before you send it."
        />
      </div>

      <div v-reveal="{ delay: 120 }" class="look">
        <div class="look__copy">
          <h3 class="sl-display look__title">See the look before it&rsquo;s built</h3>
          <p class="look__body">
            Tap a style, colours, fonts and light or dark. A small preview shows them on your
            app&rsquo;s own name, so you know what you are getting before the first build
            starts. Skip it and Imagi picks a look that fits.
          </p>
        </div>
        <div class="sl-stage look__shot">
          <ProductShot
            src="/product/create-look.webp"
            alt="The Set the look step: style, colour, font and light or dark choices, with a small preview of Ticker Insights in the chosen styling."
            :width="1560"
            :height="1270"
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
        { title: 'Name it', body: 'The name of your app.' },
        { title: 'What is your app?', body: 'A few sentences on what it is, who it’s for, and what it should help them do.' },
        { title: 'How does it work?', body: 'What people can do on it and what it keeps track of. Imagi turns this into the plan.' },
        { title: 'Set the look', body: 'Optional. A starter design, previewed on your app’s own name.' }
      ]
    }
  }
})
</script>

<style scoped>
/* A softer pool of light at the top of the step, as on steps 02 and 03 */
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

/* The form's four questions, in a row on a hairline, numbered like the form */
.brief-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0;
  margin: clamp(48px, 6vw, 72px) 0 0;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--sl-line);
}

.brief-step {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  padding: 24px clamp(16px, 2vw, 28px) 0 0;
}

.brief-step + .brief-step {
  padding-left: clamp(16px, 2vw, 28px);
  border-left: 1px solid var(--sl-line);
}

.brief-step__num {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  color: var(--sl-muted);
  font-variant-numeric: tabular-nums;
}

.brief-step .brief-step__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.brief-step__body {
  margin: 0;
  font-size: 15px;
  color: var(--sl-muted);
  text-wrap: pretty;
}

/* Set the look: the words on one side, its screenshot on the other */
.look {
  display: grid;
  grid-template-columns: minmax(0, 5fr) minmax(0, 7fr);
  gap: clamp(32px, 5vw, 72px);
  align-items: center;
  margin-top: clamp(64px, 8vw, 104px);
}

.look .look__shot {
  margin-top: 0;
}

.look .look__title {
  margin: 0;
  font-size: clamp(26px, 2.6vw, 34px);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.1;
}

.look__body {
  margin: 16px 0 0;
  max-width: 40ch;
  color: var(--sl-muted);
}

@media (max-width: 900px) {
  .brief-steps {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    row-gap: 24px;
  }

  .brief-step:nth-child(3) {
    padding-left: 0;
    border-left: 0;
  }

  .look {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 560px) {
  .brief-steps {
    grid-template-columns: minmax(0, 1fr);
  }

  .brief-step + .brief-step {
    padding-left: 0;
    border-left: 0;
  }
}
</style>
