<!-- CTA Section - full-canvas editorial finale that bookends the hero -->
<template>
  <section class="relative py-28 sm:py-36 px-6 sm:px-8 lg:px-12 transition-colors duration-500">

    <!-- One warm wash behind the headline, echoing the hero's apricot glow -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="cta-glow-warm absolute top-8 left-1/2 -translate-x-1/2 w-[760px] h-[440px]"></div>
    </div>

    <div class="relative max-w-6xl mx-auto">

      <!-- Hairline divider -->
      <div class="section-divider mb-20 md:mb-24" aria-hidden="true"></div>

      <div v-reveal class="max-w-3xl mx-auto text-center">

        <!-- Headline: the largest type after the hero, closing on the same voice -->
        <h2 class="font-display text-5xl sm:text-6xl md:text-[4.5rem] font-semibold text-blue-950 dark:text-white mb-7 tracking-[-0.02em] leading-[1.05] text-balance transition-colors duration-300">
          {{ titleLead }} <em class="cta-accent not-italic">{{ titleAccent }}</em>
        </h2>

        <p class="text-lg sm:text-xl text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty mb-11 max-w-xl mx-auto transition-colors duration-300">
          {{ description }}
        </p>

        <!-- Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <router-link
            :to="getAuthenticatedRedirect"
            class="group inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          >
            <span>{{ primaryButtonText }}</span>
            <svg class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </router-link>

          <router-link
            v-if="showSecondaryButton"
            :to="secondaryButtonTo"
            class="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-full font-medium text-lg border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          >
            <span>{{ secondaryButtonText }}</span>
          </router-link>
        </div>

        <!-- Footnote set as a folio line: serif italic between hairlines -->
        <p v-if="footnote" class="mt-10 flex items-center justify-center gap-4 text-sm">
          <span aria-hidden="true" class="h-px w-10 bg-blue-950/20 dark:bg-white/20"></span>
          <span class="font-display italic text-blue-950/70 dark:text-blue-100/55">{{ footnote }}</span>
          <span aria-hidden="true" class="h-px w-10 bg-blue-950/20 dark:bg-white/20"></span>
        </p>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, computed } from 'vue'
import { useAuthStore } from '@/shared/stores/auth'
import reveal from '@/apps/home/directives/reveal'

export default defineComponent({
  name: 'CTASection',
  directives: { reveal },
  props: {
    title: {
      type: String,
      default: 'Ready to build?'
    },
    description: {
      type: String,
      default: 'Build your web app and run your business—marketing, sales, and finance—all in one place. Start for free today.'
    },
    primaryButtonText: {
      type: String,
      default: 'Get Started'
    },
    primaryButtonTo: {
      type: [String, Object],
      default: '/imagi/projects'
    },
    showSecondaryButton: {
      type: Boolean,
      default: false
    },
    secondaryButtonText: {
      type: String,
      default: 'Learn More'
    },
    secondaryButtonTo: {
      type: [String, Object],
      default: '/docs'
    },
    footnote: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated)

    const getAuthenticatedRedirect = computed(() => {
      return isAuthenticated.value
        ? (typeof props.primaryButtonTo === 'string' ? props.primaryButtonTo : '/imagi/projects')
        : '/auth/signin'
    })

    // Split the title so its final word carries the italic gradient accent
    const titleLead = computed(() => props.title.split(' ').slice(0, -1).join(' '))
    const titleAccent = computed(() => props.title.split(' ').slice(-1)[0])

    return {
      isAuthenticated,
      getAuthenticatedRedirect,
      titleLead,
      titleAccent
    }
  }
})
</script>

<style scoped>
/* Hairline gradient divider that fades at the edges */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(23, 37, 84, 0.12), transparent);
}

.dark .section-divider {
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}

/* Soft warm wash mirroring the hero's apricot glow at half strength */
.cta-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.11), rgba(251, 146, 60, 0.03) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .cta-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.06), rgba(251, 146, 60, 0.02) 55%, transparent 75%);
}

/* Italic serif accent with the hero's warm gradient ink */
.cta-accent {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em;
}

.dark .cta-accent {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}
</style>
