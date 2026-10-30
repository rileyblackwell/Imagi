<!--
  Closing — a Spotlight page ends where the home page began: under a
  spotlight, with the same prompt box. Pricing (or the page's own sibling)
  stays one quiet link away. Home, About, Terms and Privacy all close here.
-->
<template>
  <section
    class="relative isolate overflow-hidden pb-[clamp(90px,11vw,150px)] pt-[clamp(110px,14vw,190px)] text-center"
  >
    <!-- The light sits over the headline here, not at the top edge. The !
         utilities override .sl-spot / .sl-dots, which set the same properties. -->
    <div
      class="sl-spot
        ![background:radial-gradient(ellipse_38%_48%_at_50%_30%,var(--sl-spot-core)_0%,var(--sl-spot-mid)_45%,transparent_75%),radial-gradient(ellipse_30%_25%_at_50%_100%,var(--sl-spot-wide),transparent_70%)]
        before:!top-0 before:!h-[70%]
        before:![mask-image:radial-gradient(ellipse_50%_60%_at_50%_40%,#000_20%,transparent_75%)]"
      aria-hidden="true"
    ></div>
    <div
      class="sl-dots ![mask-image:radial-gradient(ellipse_45%_50%_at_50%_42%,#000_0%,transparent_75%)]"
      aria-hidden="true"
    ></div>

    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow">Get started</p>
        <h2 class="sl-display sl-h2 !text-[length:clamp(42px,6.4vw,88px)]">{{ title }}</h2>
        <p class="sl-lede">{{ description }}</p>
      </div>

      <div v-reveal="{ delay: 80 }" class="mx-auto mb-0 mt-[34px] max-w-[620px] text-left">
        <IdeaPrompt input-id="closing-idea" size="md" :submit-label="primaryButtonText" />
      </div>

      <div v-reveal="{ delay: 120 }" class="mt-[26px] flex flex-col items-center gap-[14px] text-[15px] text-sl-muted">
        <router-link
          :to="secondaryButtonTo"
          class="border-b border-b-sl-line-strong pb-[2px] font-semibold text-sl-text [text-decoration:none]
            transition-[border-color] duration-200 ease-[ease] hover:border-b-sl-focus"
        >{{ secondaryButtonText }}</router-link>
        <span>{{ footnote }}</span>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'
import IdeaPrompt from '@/apps/home/components/molecules/IdeaPrompt.vue'

export default defineComponent({
  name: 'ClosingSection',
  components: { IdeaPrompt },
  directives: { reveal },
  props: {
    title: { type: String, default: 'Start your business today' },
    description: {
      type: String,
      default: 'A sentence about your idea is all it takes.'
    },
    primaryButtonText: { type: String, default: 'Start building' },
    secondaryButtonText: { type: String, default: 'See pricing' },
    secondaryButtonTo: { type: [String, Object], default: '/payments/pricing' },
    footnote: { type: String, default: 'Free to use. No card needed.' }
  }
})
</script>
