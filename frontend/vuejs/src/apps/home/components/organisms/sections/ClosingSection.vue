<!--
  Closing — a Spotlight page ends where the home page began: under a
  spotlight, with the same prompt box. Pricing (or the page's own sibling)
  stays one quiet link away. Home, About, Terms and Privacy all close here.
-->
<template>
  <section class="closing">
    <div class="sl-spot closing__spot" aria-hidden="true"></div>
    <div class="sl-dots closing__dots" aria-hidden="true"></div>

    <div class="sl-wrap">
      <div v-reveal class="sl-head">
        <p class="sl-eyebrow">Get started</p>
        <h2 class="sl-display sl-h2 closing__title">{{ title }}</h2>
        <p class="sl-lede">{{ description }}</p>
      </div>

      <div v-reveal="{ delay: 80 }" class="closing__prompt">
        <IdeaPrompt input-id="closing-idea" size="md" :submit-label="primaryButtonText" />
      </div>

      <div v-reveal="{ delay: 120 }" class="closing__links">
        <router-link :to="secondaryButtonTo" class="closing__link">{{ secondaryButtonText }}</router-link>
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
      default: 'Describe what you want to build, and have a working web app the same afternoon — with the tools to market, sell and run it waiting in the same project.'
    },
    primaryButtonText: { type: String, default: 'Start building' },
    secondaryButtonText: { type: String, default: 'See pricing' },
    secondaryButtonTo: { type: [String, Object], default: '/payments/pricing' },
    footnote: { type: String, default: 'Start for free. Upgrade anytime as you grow.' }
  }
})
</script>

<style scoped>
.closing {
  position: relative;
  isolation: isolate;
  overflow: hidden;
  padding-block: clamp(110px, 14vw, 190px) clamp(90px, 11vw, 150px);
  text-align: center;
}

/* The light sits over the headline here, not at the top edge */
.closing .closing__spot {
  background:
    radial-gradient(ellipse 38% 48% at 50% 30%, var(--sl-spot-core) 0%, var(--sl-spot-mid) 45%, transparent 75%),
    radial-gradient(ellipse 30% 25% at 50% 100%, var(--sl-spot-wide), transparent 70%);
}

.closing .closing__spot::before {
  top: 0;
  height: 70%;
  -webkit-mask-image: radial-gradient(ellipse 50% 60% at 50% 40%, #000 20%, transparent 75%);
  mask-image: radial-gradient(ellipse 50% 60% at 50% 40%, #000 20%, transparent 75%);
}

.closing .closing__dots {
  -webkit-mask-image: radial-gradient(ellipse 45% 50% at 50% 42%, #000 0%, transparent 75%);
  mask-image: radial-gradient(ellipse 45% 50% at 50% 42%, #000 0%, transparent 75%);
}

.closing .closing__title {
  font-size: clamp(42px, 6.4vw, 88px);
}

.closing__prompt {
  max-width: 620px;
  margin: 34px auto 0;
  text-align: left;
}

.closing__links {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  margin-top: 26px;
  font-size: 15px;
  color: var(--sl-muted);
}

.closing__link {
  padding-bottom: 2px;
  border-bottom: 1px solid var(--sl-line-strong);
  color: var(--sl-text);
  font-weight: 600;
  text-decoration: none;
  transition: border-color 0.2s ease;
}

.closing__link:hover {
  border-bottom-color: var(--sl-focus);
}
</style>
