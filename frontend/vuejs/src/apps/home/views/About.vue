<!--
  About page — on the home page's Spotlight stage.

  Deeper than the homepage, lighter than the docs. It follows the same order a
  founder works in (why, 01 Start, 02 Build, 03 Run, then plans) and borrows
  the homepage's shapes: centred section heads, the step row on a hairline,
  Spotlight cards with highlights, one workspace shot on stage, and the fact
  row. Light and dark come from shared/styles/spotlight.css.
-->
<template>
  <div class="spotlight about-page">
    <DefaultLayout>
      <!-- Opening statement -->
      <section class="sl-opener">
        <div class="sl-spot" aria-hidden="true"></div>
        <div class="sl-dots" aria-hidden="true"></div>

        <div class="sl-wrap sl-opener__inner">
          <p class="about-rise sl-eyebrow sl-pill">
            <span class="sl-pip" aria-hidden="true"></span>
            <span>About Imagi</span>
          </p>
          <h1 class="about-rise sl-display sl-h1 about-title" style="animation-delay: 60ms">
            An idea is <em class="sl-run">enough</em>
          </h1>
          <p class="about-rise sl-lede" style="animation-delay: 120ms">
            Imagi is where you make a web app by describing it, and where you run the
            business that grows around it. Here is how that works, from the first brief
            to the first customer.
          </p>
        </div>
      </section>

      <!-- Why Imagi exists -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow">Why Imagi</p>
            <h2 class="sl-display sl-h2">Building the app shouldn&rsquo;t be the hard part</h2>
            <p class="sl-lede">
              Good ideas tend to stall at the same place: someone has to write the software.
              Imagi&rsquo;s agents take that part on, so you can spend your time on the idea
              and the people it&rsquo;s for.
            </p>
          </div>

          <ul v-reveal="{ delay: 60 }" class="about-row">
            <li v-for="item in principles" :key="item.title" class="about-row__item">
              <h3 class="about-row__title">{{ item.title }}</h3>
              <p class="about-row__body">{{ item.body }}</p>
            </li>
          </ul>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- 01 Start -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow"><span class="sl-grad-text about-num">01</span><span>Start</span></p>
            <h2 class="sl-display sl-h2">From a brief to a first version</h2>
            <p class="sl-lede">
              A project starts with four questions: your app&rsquo;s name, what it is, how it
              works, and, if you like, how it should look. Once you create it, Imagi builds
              without waiting on you.
            </p>
          </div>

          <ol v-reveal="{ delay: 60 }" class="about-row">
            <li v-for="item in firstBuild" :key="item.title" class="about-row__item">
              <span class="about-row__label">{{ item.when }}</span>
              <h3 class="about-row__title">{{ item.title }}</h3>
              <p class="about-row__body">{{ item.body }}</p>
            </li>
          </ol>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- 02 Build -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow"><span class="sl-grad-text about-num">02</span><span>Build</span></p>
            <h2 class="sl-display sl-h2">How the workspace works</h2>
            <p class="sl-lede">
              Your conversation sits on the left and your running app on the right. Behind
              the chat, a coordinator and its threads share the work.
            </p>
          </div>

          <ul v-reveal="{ delay: 60 }" class="about-row about-row--3">
            <li v-for="item in workspace" :key="item.title" class="about-row__item">
              <h3 class="about-row__title">{{ item.title }}</h3>
              <p class="about-row__body">{{ item.body }}</p>
            </li>
          </ul>

          <div v-reveal="{ delay: 120 }" class="sl-stage about-shot">
            <ProductShot
              src="/product/build-workspace.webp"
              alt="The Imagi build workspace: the coordinator has split a request into two threads, one finished and one still working, and on the right the live stock-tracking app it wrote."
              :width="2400"
              :height="1500"
              label="imagi — build workspace"
            />
          </div>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- 03 Run -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow">
              <span class="sl-grad-text about-num">03</span><span>Run</span><StatusBadge tone="neutral" label="Beta" />
            </p>
            <h2 class="sl-display sl-h2">The business side, in the same project</h2>
            <p class="sl-lede">
              Every project also has three workspaces for running the business. They connect
              to accounts you own, so the money and the messages stay yours. All three are
              in beta: they work today and are still growing.
            </p>
          </div>

          <div class="sl-cards">
            <article
              v-for="(tool, index) in tools"
              :key="tool.title"
              v-reveal="{ delay: 80 + index * 80 }"
              class="sl-card"
            >
              <span class="sl-card__icon"><LineIcon :name="tool.icon" /></span>
              <h3 class="sl-card__title">{{ tool.title }}</h3>
              <p class="sl-card__body">{{ tool.description }}</p>
              <ul class="sl-highlights">
                <li v-for="highlight in tool.highlights" :key="highlight">{{ highlight }}</li>
              </ul>
            </article>
          </div>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- Plans, and what isn't here yet -->
      <section class="sl-sec about-step">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow">Good to know</p>
            <h2 class="sl-display sl-h2">What it costs, and what&rsquo;s next</h2>
            <p class="sl-lede">
              Every plan comes with a weekly allowance of AI usage. Which model you pick and
              how hard it thinks decide how far that goes.
            </p>
          </div>

          <dl v-reveal="{ delay: 60 }" class="about-facts">
            <div v-for="fact in facts" :key="fact.label" class="about-fact">
              <dt class="about-fact__label">{{ fact.label }}</dt>
              <dd class="about-fact__value sl-display sl-grad-text">{{ fact.value }}</dd>
              <p class="about-fact__caption">{{ fact.caption }}</p>
            </div>
          </dl>

          <p v-reveal="{ delay: 120 }" class="about-next">
            <span class="about-row__label">Not yet</span>
            <span>
              Publishing your app to the web from Imagi isn&rsquo;t available yet. It&rsquo;s
              being built, along with more for Sell, Market and Operate.
            </span>
          </p>
        </div>
      </section>

      <ClosingSection
        title="Try it on your idea"
        description="Start with a sentence about what you want to make. When you want every detail, the docs cover each step in full."
        primary-button-text="Start building"
        secondary-button-text="Read the docs"
        secondary-button-to="/docs"
      />
    </DefaultLayout>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { ClosingSection } from '@/apps/home/components/organisms/sections'
import { ProductShot } from '@/apps/home/components/atoms'
import { LineIcon, StatusBadge } from '@/shared/components'
import reveal from '@/apps/home/directives/reveal'

export default defineComponent({
  name: 'About',
  components: {
    DefaultLayout,
    ClosingSection,
    ProductShot,
    LineIcon,
    StatusBadge
  },
  directives: { reveal },
  setup() {
    const principles = [
      { title: 'You describe it', body: 'Requests are plain words. The agents plan the work, write the code and check it.' },
      { title: 'Real code underneath', body: 'Every app is a standard Vue and Django codebase, not a closed format.' },
      { title: 'You stay in charge', body: 'Agents ask when a choice is yours, and you can stop any run and keep what’s done.' },
      { title: 'One project', body: 'The app and the tools to run the business live side by side.' }
    ]

    const firstBuild = [
      { when: 'About a minute', title: 'The home page', body: 'Built first, in fast mode, so you can step into the workspace almost right away.' },
      { when: 'Side by side', title: 'The rest of the plan', body: 'Imagi works out the other pages your app needs, usually five to twenty, and builds them at once.' },
      { when: 'Built in', title: 'Secure sign-in', body: 'Sign-in and register pages come prebuilt and tested, then get restyled to match your home page.' },
      { when: 'About 10 minutes', title: 'A first version', body: 'Pages appear in your app as they finish. From there you keep shaping it by chatting.' }
    ]

    const workspace = [
      { title: 'The coordinator', body: 'Your one conversation. It answers questions itself and turns each request into a job for a thread.' },
      { title: 'Threads', body: 'Each job gets its own thread, up to five at a time. Open one to follow or steer it. It keeps going if you close the tab.' },
      { title: 'A live preview', body: 'Your app runs beside the chat and changes as files are written. The agents click and type in it to check their own work.' },
      { title: 'Questions, not guesses', body: 'When a decision is yours, the agent asks in the chat, often with answers you can tap.' },
      { title: 'Errors get fixed', body: 'If your app throws an error, it goes back to the thread that caused it, or to a new thread that fixes it.' },
      { title: 'Your choice of model', body: 'Pick one of four Claude models and five levels of effort. Opus 5.5 at Medium is the default.' }
    ]

    const tools = [
      {
        title: 'Sell',
        description: 'Connect Stripe, choose how you charge, and Imagi adds secure payment pages to your app. Card details never touch your app, and the money lands in your Stripe account.',
        icon: 'sales',
        highlights: ['One-time, subscription or pay as you go', 'Orders and customers in one place', 'Prebuilt, locked payment pages']
      },
      {
        title: 'Market',
        description: 'Send text campaigns to your contacts over your own Twilio account and answer replies in one inbox. Google search ads can be planned now and launched once Google Ads is connected.',
        icon: 'marketing',
        highlights: ['Text campaigns and an inbox', 'Contacts with consent built in', 'Google search ad drafts']
      },
      {
        title: 'Operate',
        description: 'One dashboard with two halves. Your app: whether it’s up, how fast it answers and who’s visiting. Your business: revenue, expenses and profit.',
        icon: 'finance',
        highlights: ['Uptime and response time', 'Visitors, counted without cookies', 'Revenue, expenses and profit']
      }
    ]

    const facts = [
      { label: 'Plans start at', value: 'Free', caption: 'Free usage every week. Paid plans add more.' },
      { label: 'Markup on AI usage', value: '0%', caption: 'Usage is metered at the AI providers’ own prices.' },
      { label: 'Per run', value: '$10', caption: 'A run that reaches it stops and checks in with you first.' }
    ]

    return { principles, firstBuild, workspace, tools, facts }
  }
})
</script>

<style scoped>
/* Staggered entrance on load, as on the home hero */
.about-rise {
  animation: about-rise 0.85s var(--app-ease) both;
}

@keyframes about-rise {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.sl-opener .about-title {
  max-width: 11ch;
  margin-top: 6px;
}

.about-num {
  font-weight: 700;
}

/* A softer pool of light at the top of each section, as on Home's steps */
.about-step {
  isolation: isolate;
  overflow: hidden;
}

.about-step::before {
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

/* The homepage's step row: items on one hairline, divided by vertical
   hairlines. Four across by default; --3 makes a three-across grid whose
   second row gets its own hairline. */
.about-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin: clamp(48px, 6vw, 72px) 0 0;
  padding: 0;
  list-style: none;
  border-top: 1px solid var(--sl-line);
}

.about-row__item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
  padding: 24px clamp(16px, 2vw, 28px) 0;
  border-left: 1px solid var(--sl-line);
}

.about-row__item:first-child {
  padding-left: 0;
  border-left: 0;
}

.about-row--3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
  row-gap: 0;
}

.about-row--3 .about-row__item {
  padding-bottom: 28px;
}

.about-row--3 .about-row__item:nth-child(3n + 1) {
  padding-left: 0;
  border-left: 0;
}

.about-row--3 .about-row__item:nth-child(n + 4) {
  border-top: 1px solid var(--sl-line);
}

.about-row__label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.about-row .about-row__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.about-row__body {
  margin: 0;
  font-size: 15px;
  color: var(--sl-muted);
  text-wrap: pretty;
}

/* One workspace shot, held narrower than the text, as on Home */
.about-shot {
  max-width: 920px;
  margin-inline: auto;
}

/* The homepage's fact row: three centred cells between two hairlines */
.about-facts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  margin: clamp(48px, 6vw, 72px) 0 0;
  border-top: 1px solid var(--sl-line);
  border-bottom: 1px solid var(--sl-line);
}

.about-fact {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: clamp(32px, 4vw, 44px) clamp(16px, 2.4vw, 32px);
  text-align: center;
}

.about-fact + .about-fact {
  border-left: 1px solid var(--sl-line);
}

.about-fact__label {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.about-fact .about-fact__value {
  margin: 0;
  font-size: clamp(44px, 5.2vw, 72px);
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.045em;
  font-variant-numeric: tabular-nums;
  filter: drop-shadow(0 0 30px var(--sl-text-glow));
}

.about-fact__caption {
  margin: 0;
  max-width: 30ch;
  font-size: 15px;
  color: var(--sl-muted);
  text-wrap: pretty;
}

/* What isn't built yet: one quiet line under the facts */
.about-next {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: center;
  gap: 8px 16px;
  max-width: 760px;
  margin: 32px auto 0;
  font-size: 15px;
  color: var(--sl-muted);
  text-align: center;
  text-wrap: pretty;
}

@media (max-width: 900px) {
  .about-row,
  .about-row--3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    row-gap: 24px;
  }

  .about-row--3 {
    row-gap: 0;
  }

  .about-row__item:nth-child(odd),
  .about-row--3 .about-row__item:nth-child(odd) {
    padding-left: 0;
    border-left: 0;
  }

  .about-row__item:nth-child(even),
  .about-row--3 .about-row__item:nth-child(even) {
    padding-left: clamp(16px, 2vw, 28px);
    border-left: 1px solid var(--sl-line);
  }

  .about-row--3 .about-row__item:nth-child(n + 3) {
    border-top: 1px solid var(--sl-line);
  }

  .about-facts {
    grid-template-columns: minmax(0, 1fr);
  }

  .about-fact + .about-fact {
    border-left: 0;
    border-top: 1px solid var(--sl-line);
  }
}

@media (max-width: 560px) {
  .about-row,
  .about-row--3 {
    grid-template-columns: minmax(0, 1fr);
  }

  .about-row__item,
  .about-row__item:nth-child(even),
  .about-row--3 .about-row__item:nth-child(even) {
    padding-left: 0;
    border-left: 0;
  }

  .about-row--3 .about-row__item:nth-child(n + 2) {
    border-top: 1px solid var(--sl-line);
  }
}

@media (prefers-reduced-motion: reduce) {
  .about-rise {
    animation: none;
  }
}
</style>
