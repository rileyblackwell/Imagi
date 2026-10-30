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
          <!-- mt is important: .sl-display zeroes the margin -->
          <h1 class="about-rise sl-display sl-h1 max-w-[11ch] !mt-[6px]" style="animation-delay: 60ms">
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
      <section class="sl-sec" :class="stepSection">
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

          <ul v-reveal="{ delay: 60 }" :class="[row, 'grid-cols-4 max-[900px]:gap-y-6']">
            <li v-for="(item, i) in principles" :key="item.title" :class="rowItem(i, 4)">
              <h3 :class="rowTitle">{{ item.title }}</h3>
              <p :class="rowBody">{{ item.body }}</p>
            </li>
          </ul>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- 01 Start -->
      <section class="sl-sec" :class="stepSection">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow"><span class="sl-grad-text font-bold">01</span><span>Start</span></p>
            <h2 class="sl-display sl-h2">From a brief to a first version</h2>
            <p class="sl-lede">
              A project starts with four questions: your app&rsquo;s name, what it is, how it
              works, and, if you like, how it should look. Once you create it, Imagi builds
              without waiting on you.
            </p>
          </div>

          <ol v-reveal="{ delay: 60 }" :class="[row, 'grid-cols-4 max-[900px]:gap-y-6']">
            <li v-for="(item, i) in firstBuild" :key="item.title" :class="rowItem(i, 4)">
              <span :class="label">{{ item.when }}</span>
              <h3 :class="rowTitle">{{ item.title }}</h3>
              <p :class="rowBody">{{ item.body }}</p>
            </li>
          </ol>
        </div>
      </section>

      <div class="sl-divider" aria-hidden="true"></div>

      <!-- 02 Build -->
      <section class="sl-sec" :class="stepSection">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow"><span class="sl-grad-text font-bold">02</span><span>Build</span></p>
            <h2 class="sl-display sl-h2">How the workspace works</h2>
            <p class="sl-lede">
              Your conversation sits on the left and your running app on the right. Behind
              the chat, a coordinator and its threads share the work.
            </p>
          </div>

          <ul v-reveal="{ delay: 60 }" :class="[row, 'grid-cols-3 gap-y-0']">
            <li v-for="(item, i) in workspace" :key="item.title" :class="rowItem(i, 3)">
              <h3 :class="rowTitle">{{ item.title }}</h3>
              <p :class="rowBody">{{ item.body }}</p>
            </li>
          </ul>

          <!-- One workspace shot, held narrower than the text, as on Home -->
          <div v-reveal="{ delay: 120 }" class="sl-stage mx-auto max-w-[920px]">
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
      <section class="sl-sec" :class="stepSection">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow">
              <span class="sl-grad-text font-bold">03</span><span>Run</span><StatusBadge tone="neutral" label="Beta" />
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

      <!-- What it costs, and what isn't here yet -->
      <section class="sl-sec" :class="stepSection">
        <div class="sl-wrap">
          <div v-reveal class="sl-head">
            <p class="sl-eyebrow">Good to know</p>
            <h2 class="sl-display sl-h2">What it costs, and what&rsquo;s next</h2>
            <p class="sl-lede">
              Imagi is free, with no weekly limit on AI usage. One safeguard stays: a single
              run that gets expensive checks in with you before it goes further.
            </p>
          </div>

          <!-- The homepage's fact row: three centred cells between two hairlines -->
          <dl
            v-reveal="{ delay: 60 }"
            class="mx-0 mb-0 mt-[clamp(48px,6vw,72px)] grid grid-cols-3 border-y border-y-sl-line max-[900px]:grid-cols-1"
          >
            <div
              v-for="(fact, i) in facts"
              :key="fact.label"
              class="flex min-w-0 flex-col items-center gap-3 px-[clamp(16px,2.4vw,32px)] py-[clamp(32px,4vw,44px)] text-center"
              :class="{
                'border-l border-l-sl-line max-[900px]:border-t max-[900px]:border-t-sl-line max-[900px]:[border-left:0]':
                  i > 0
              }"
            >
              <dt :class="label">{{ fact.label }}</dt>
              <!-- m and font-weight are important: .sl-display and .sl-grad-text set them -->
              <dd
                class="sl-display sl-grad-text !m-0 text-[length:clamp(44px,5.2vw,72px)] !font-bold leading-none
                  tracking-[-0.045em] tabular-nums drop-shadow-[0_0_30px_var(--sl-text-glow)]"
              >{{ fact.value }}</dd>
              <p class="m-0 max-w-[30ch] text-[15px] text-sl-muted text-pretty">{{ fact.caption }}</p>
            </div>
          </dl>

          <!-- What isn't built yet: one quiet line under the facts -->
          <p
            v-reveal="{ delay: 120 }"
            class="mx-auto mb-0 mt-8 flex max-w-[760px] flex-wrap items-baseline justify-center gap-x-4 gap-y-2
              text-center text-[15px] text-sl-muted text-pretty"
          >
            <span :class="label">Not yet</span>
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
      { when: 'About 5 seconds', title: 'The home page', body: 'Your app opens in the workspace with its home page on screen, and a fuller version replaces it moments later.' },
      { when: 'Side by side', title: 'The rest of the plan', body: 'Imagi works out the other pages your app needs, usually five to twenty, and builds them at once.' },
      { when: 'Built in', title: 'Secure sign-in', body: 'Sign-in and register pages come prebuilt and tested, then get restyled to match your home page.' },
      { when: 'A few minutes', title: 'A first version', body: 'Pages appear in your app as they finish. From there you keep shaping it by chatting.' }
    ]

    const workspace = [
      { title: 'The coordinator', body: 'Your one conversation. It answers questions itself and turns each request into a job for a thread.' },
      { title: 'Threads', body: 'Each job gets its own thread, up to five at a time. Open one to follow or steer it. It keeps going if you close the tab.' },
      { title: 'A live preview', body: 'Your app runs beside the chat and changes as files are written. The agents click and type in it to check their own work.' },
      { title: 'Questions, not guesses', body: 'When a decision is yours, the agent asks in the chat, often with answers you can tap.' },
      { title: 'Errors get fixed', body: 'If your app throws an error, it goes back to the thread that caused it, or to a new thread that fixes it.' },
      { title: 'Your choice of model', body: 'Pick a Claude or OpenAI model and how hard it thinks, with faster speeds on OpenAI. Opus 5.5 at Medium is the default.' }
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
      { label: 'Price', value: 'Free', caption: 'One open plan: no usage limit, as many projects as you need.' },
      { label: 'Markup on AI usage', value: '0%', caption: 'Usage is metered at the AI providers’ own prices.' },
      { label: 'Per run', value: '$10', caption: 'A run that reaches it stops and checks in with you first.' }
    ]

    // A softer pool of light at the top of each section, as on Home's steps
    const stepSection = `isolate overflow-hidden
      before:pointer-events-none before:absolute before:left-1/2 before:top-0 before:z-[-1] before:h-[560px]
      before:w-[min(1100px,140vw)] before:-translate-x-1/2 before:content-['']
      before:bg-[radial-gradient(ellipse_50%_60%_at_50%_0%,var(--sl-section-glow),transparent_70%)]`

    // The homepage's step row: items on one hairline, divided by vertical
    // hairlines. Four or three across, two at 900px and below, one at 560px.
    const row = 'mx-0 mb-0 mt-[clamp(48px,6vw,72px)] grid list-none border-t border-t-sl-line p-0 max-[900px]:grid-cols-2 max-[560px]:grid-cols-1'
    const label = 'text-[12px] font-semibold uppercase tracking-[0.18em] text-sl-muted'
    const rowTitle = 'about-row__title m-0 text-[18px] font-semibold tracking-[-0.01em]'
    const rowBody = 'm-0 text-[15px] text-sl-muted text-pretty'

    // An item that starts a row drops its left hairline and padding. In the
    // three-across grid every later row gets its own top hairline; the
    // four-across row only ever has one row of four.
    const rowItem = (i, across) => [
      'flex min-w-0 flex-col gap-2 px-[clamp(16px,2vw,28px)] pt-6 max-[560px]:pl-0 max-[560px]:[border-left:0]',
      across === 3 ? 'pb-7' : 'pb-0',
      (across === 3 ? i % 3 === 0 : i === 0) ? 'pl-0 [border-left:0]' : 'border-l border-l-sl-line',
      i % 2 === 0
        ? 'max-[900px]:pl-0 max-[900px]:[border-left:0]'
        : 'max-[900px]:pl-[clamp(16px,2vw,28px)] max-[900px]:[border-left:1px_solid_var(--sl-line)]',
      across === 3 && i >= 3 && 'border-t border-t-sl-line',
      across === 3 && i === 2 && 'max-[900px]:border-t max-[900px]:border-t-sl-line',
      across === 3 && i === 1 && 'max-[560px]:border-t max-[560px]:border-t-sl-line'
    ]

    return { principles, firstBuild, workspace, tools, facts, stepSection, row, label, rowTitle, rowBody, rowItem }
  }
})
</script>

<style scoped>
/* Staggered entrance on load, as on the home hero. Stays CSS: a scoped
   @keyframes name is hashed, so a utility can't reference it. */
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

@media (prefers-reduced-motion: reduce) {
  .about-rise {
    animation: none;
  }
}
</style>
