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

      <!-- Same prompt as the hero, so the page closes on the action it opened
           with. Pricing stays one quiet link away. -->
      <div v-reveal="{ delay: 80 }" class="closing-prompt mt-11">
        <IdeaPrompt input-id="closing-idea" size="md" :submit-label="primaryButtonText" />
        <router-link v-if="showSecondaryButton" :to="secondaryButtonTo" class="btn-quiet mt-5">
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
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import IdeaPrompt from '@/apps/home/components/molecules/IdeaPrompt.vue'

export default defineComponent({
  name: 'CTASection',
  components: { IdeaPrompt },
  directives: { reveal },
  props: {
    title: { type: String, default: 'Start your business today' },
    description: {
      type: String,
      default: 'Describe what you want to build, and have a working web app the same afternoon — with the tools to market, sell and run it waiting in the same project.'
    },
    primaryButtonText: { type: String, default: 'Start building' },
    showSecondaryButton: { type: Boolean, default: true },
    secondaryButtonText: { type: String, default: 'See pricing' },
    secondaryButtonTo: { type: [String, Object], default: '/payments/pricing' },
    footnote: { type: String, default: 'Start for free. Upgrade anytime as you grow.' }
  }
})
</script>

<style scoped>
.closing-rule {
  height: 1px;
  background: var(--rule-strong);
}

.closing-prompt {
  max-width: 44rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.closing-prompt > :first-child {
  align-self: stretch;
}

.footnote {
  margin-top: 3.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--rule);
  font-size: 0.85rem;
  color: var(--ink-40);
}
</style>
