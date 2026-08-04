<!--
  Closing CTA.

  Previously an inverted panel, which on paper read as a big navy box dropped
  onto the page rather than part of it. This version is built from the same
  parts as every other section — rule, eyebrow, headline-left/copy-right — and
  simply runs at the largest scale on the page after the hero. The page opens
  and closes on the same shape, and ends on paper, so the handoff to the footer
  is a hairline rather than a hard edge.
-->
<template>
  <section class="relative py-20 md:py-28">
    <div class="section-shell">
      <!-- Slightly stronger than the section rules above it: the only signal
           that this is the closing movement rather than another section. -->
      <div class="closing-rule mb-14 md:mb-16" aria-hidden="true"></div>

      <div v-reveal class="md:flex md:items-end md:justify-between gap-12 lg:gap-16">
        <div class="max-w-[34rem]">
          <p class="eyebrow">
            <span class="eyebrow__mark" aria-hidden="true"></span>
            <span class="eyebrow__rule" aria-hidden="true"></span>
            <span>Get started</span>
          </p>
          <h2 class="display mt-6 text-[2.6rem] sm:text-5xl md:text-[3.6rem]">
            {{ title }}
          </h2>
        </div>

        <p class="lede mt-6 md:mt-0 md:max-w-sm md:pb-3 text-lg">
          {{ description }}
        </p>
      </div>

      <div v-reveal="{ delay: 80 }" class="mt-11 flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-7">
        <router-link :to="getAuthenticatedRedirect" class="btn-primary group">
          <span>{{ primaryButtonText }}</span>
          <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </router-link>

        <router-link v-if="showSecondaryButton" :to="secondaryButtonTo" class="btn-quiet">
          <span>{{ secondaryButtonText }}</span>
        </router-link>
      </div>

      <!-- Footnote sits on its own hairline, closing the page the way each
           section opened. -->
      <p v-if="footnote" v-reveal="{ delay: 120 }" class="footnote">
        {{ footnote }}
      </p>
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
    title: { type: String, default: 'Start your business today' },
    description: {
      type: String,
      default: 'Describe what you want to build, and have a working web app the same afternoon — with the tools to market, sell and run it waiting in the same project.'
    },
    primaryButtonText: { type: String, default: 'Start building' },
    primaryButtonTo: { type: [String, Object], default: '/imagi/projects' },
    showSecondaryButton: { type: Boolean, default: true },
    secondaryButtonText: { type: String, default: 'See pricing' },
    secondaryButtonTo: { type: [String, Object], default: '/payments/pricing' },
    footnote: { type: String, default: 'Start for free. Upgrade anytime as you grow.' }
  },
  setup(props) {
    const authStore = useAuthStore()
    const isAuthenticated = computed(() => authStore.isAuthenticated)

    const getAuthenticatedRedirect = computed(() =>
      isAuthenticated.value
        ? typeof props.primaryButtonTo === 'string'
          ? props.primaryButtonTo
          : '/imagi/projects'
        : '/auth/signin'
    )

    return { isAuthenticated, getAuthenticatedRedirect }
  }
})
</script>

<style scoped>
.closing-rule {
  height: 1px;
  background: var(--rule-strong);
}

.footnote {
  margin-top: 3.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--rule);
  font-size: 0.85rem;
  color: var(--ink-40);
}
</style>
