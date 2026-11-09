<!--
  Step 02 — Build.
  A tour of the workspace: the three things worth knowing sit in a list on the
  left, and the real screenshot on the right zooms to the part of the
  workspace the open one describes (the composer, the threads, then the whole
  workspace with the live app beside the chat).

  The list is an accordion: one item open at a time. Until the visitor picks
  one, the tour plays itself while the section is on screen; the first click or
  key press stops it for good. It never plays under reduced motion.
-->
<template>
  <section
    ref="root"
    id="build"
    class="sl-sec scroll-mt-14 isolate overflow-hidden
      before:pointer-events-none before:absolute before:left-1/2 before:top-0 before:z-[-1] before:h-[560px]
      before:w-[min(1100px,140vw)] before:-translate-x-1/2 before:content-['']
      before:bg-[radial-gradient(ellipse_50%_60%_at_50%_0%,var(--sl-section-glow),transparent_70%)]"
  >
    <!-- A softer pool of light at the top of each step -->
    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow"><span class="sl-grad-text font-bold">02</span><span>Build</span></p>
        <h2 class="sl-display sl-h2">Build your web app</h2>
        <p class="sl-lede">
          After the first build, the app keeps growing the same way: you ask, and
          Imagi&rsquo;s agents do the work.
        </p>
      </div>

      <!-- The tour: words on the left, the workspace on the right -->
      <div
        v-reveal="{ delay: 80 }"
        class="mt-[clamp(48px,6vw,72px)] grid grid-cols-[minmax(0,4fr)_minmax(0,7fr)] items-start
          gap-[clamp(32px,4.5vw,64px)] max-[900px]:grid-cols-[minmax(0,1fr)]"
      >
        <ol class="tour m-0 list-none border-l border-l-sl-line p-0">
          <li
            v-for="(feature, index) in features"
            :key="feature.title"
            class="tour__item relative pl-[clamp(18px,2vw,26px)]"
            :class="{ 'is-open': index === active }"
          >
            <!-- The lit segment of the rail, beside the open item -->
            <span
              class="pointer-events-none absolute bottom-0 left-[-1px] top-0 w-[2px] origin-top bg-sl-grad
                transition-[opacity,transform] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]
                motion-reduce:transition-none"
              :class="index === active ? 'scale-y-100 opacity-100' : 'scale-y-0 opacity-0'"
              aria-hidden="true"
            ></span>

            <h3 class="m-0">
              <button
                :id="`tour-tab-${index}`"
                type="button"
                class="tour__tab group flex w-full cursor-pointer items-center gap-[14px] border-0 bg-transparent px-0
                  py-[14px] text-left transition-colors duration-200"
                :class="index === active ? 'text-sl-text' : 'text-sl-muted hover:text-sl-text'"
                :aria-expanded="index === active"
                :aria-controls="`tour-panel-${index}`"
                @click="select(index)"
              >
                <!-- mb is important: .sl-card__icon sets its own -->
                <span
                  class="sl-card__icon !mb-0 shrink-0 transition-[border-color,color] duration-200"
                  :class="index === active ? '' : '!text-sl-muted group-hover:!text-sl-text'"
                ><LineIcon :name="feature.icon" /></span>
                <span class="sl-card__title">{{ feature.title }}</span>
              </button>
            </h3>

            <!-- grid-rows 0fr → 1fr opens the panel without measuring it -->
            <div
              :id="`tour-panel-${index}`"
              role="region"
              :aria-labelledby="`tour-tab-${index}`"
              class="grid transition-[grid-template-rows,opacity] duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]
                motion-reduce:transition-none"
              :class="index === active ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0'"
            >
              <div class="min-h-0 overflow-hidden" :inert="index !== active">
                <p class="sl-card__body max-w-[44ch] pb-4">{{ feature.description }}</p>
                <ul class="sl-highlights !mb-5">
                  <li v-for="highlight in feature.highlights" :key="highlight">{{ highlight }}</li>
                </ul>
              </div>
            </div>
          </li>
        </ol>

        <!-- mt is important: .sl-stage sets its own -->
        <div class="sl-stage !mt-0">
          <ProductShot
            src="/product/build-workspace.webp"
            alt="The Imagi build workspace: the coordinator has split a request into two threads, one finished and one still working, and on the right the live stock-tracking app it wrote, with a watchlist snapshot of AAPL, TSLA and MSFT prices."
            :width="2400"
            :height="1500"
            label="imagi — build workspace"
            :focus="features[active].focus"
            :caption="features[active].caption"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import { ProductShot } from '@/apps/home/components/atoms'
import { LineIcon } from '@/shared/components'

// How long each stop of the tour holds while it plays itself.
export const TOUR_HOLD_MS = 5200

export default defineComponent({
  name: 'FeaturesSection',
  components: { LineIcon, ProductShot },
  directives: { reveal },
  props: {
    // `focus` is the part of the workspace screenshot the feature points at
    // (see ProductShot); null shows the whole workspace.
    features: {
      type: Array,
      default: () => [
        {
          title: 'Just say what you want',
          description: 'Ask for a page, a feature or a fix in plain words. The coordinator turns it into a plan and checks with you when something is yours to decide.',
          icon: 'chat',
          highlights: ['Plain-language requests', 'Questions you answer in a tap', 'Real Vue and Django code'],
          focus: { x: 0, y: 100, scale: 2.3 },
          caption: 'The composer: say what you want next, in your own words.'
        },
        {
          title: 'Threads do the work',
          description: 'The coordinator hands the work to threads that build side by side. They keep going if you close the tab, and fixes go back to the thread that caused them.',
          icon: 'teams',
          highlights: ['Pages built in parallel', 'Fixes its own errors', 'Keeps working while you’re away'],
          focus: { x: 0, y: 49, scale: 2.3 },
          caption: 'One request, split into two threads: one finished, one still working.'
        },
        {
          title: 'A live app beside you',
          description: 'Your app runs next to the chat the whole time. The agent uses it like a person would, clicking and typing to check its own work, and so can you.',
          icon: 'design',
          highlights: ['Live preview', 'The agent drives your app', 'Changes land as they’re made'],
          focus: null,
          caption: 'A real project mid-conversation: Ticker Insights, running live beside the chat.'
        }
      ]
    }
  },
  setup(props) {
    const root = ref(null)
    const active = ref(0)
    let playing = false
    let timer = null
    let observer = null

    const pause = () => {
      if (timer) clearInterval(timer)
      timer = null
    }

    const play = () => {
      if (!playing || timer) return
      timer = setInterval(() => {
        active.value = (active.value + 1) % props.features.length
      }, TOUR_HOLD_MS)
    }

    // The visitor chose: show it, and stop playing for good.
    const select = (index) => {
      playing = false
      pause()
      observer?.disconnect()
      active.value = index
    }

    onMounted(() => {
      const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
      if (reduce || !('IntersectionObserver' in window) || !root.value) return
      playing = true
      // Only while the tour is actually on screen
      observer = new IntersectionObserver(
        ([entry]) => (entry.isIntersecting ? play() : pause()),
        { threshold: 0.35 }
      )
      observer.observe(root.value)
    })

    onBeforeUnmount(() => {
      pause()
      observer?.disconnect()
    })

    return { root, active, select }
  }
})
</script>
