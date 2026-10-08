<!--
  ImagiLogo.vue - Standardized logo component

  "Lit Dot": a lowercase "imagi" in the Spotlight display face (Bricolage
  Grotesque). Both i's are set dotless (ı) and given drawn dots, so the dot
  over the last i can be the light — a coral-to-amber point with a soft glow,
  the same gradient the homepage spends on "run". Ink in light mode, white in
  dark.

  The colours live here rather than in spotlight.css's --sl-* tokens because
  the logo also renders on pages that have no .spotlight root (pricing,
  checkout); the values match the Spotlight gradient in each theme.
-->
<template>
  <router-link :to="to" class="flex items-center" aria-label="Imagi">
    <span
      class="wordmark leading-none text-ink dark:text-white transition-colors duration-300"
      :class="[
        size === 'sm' ? 'text-lg' :
        size === 'md' ? 'text-[1.4rem]' :
        size === 'lg' ? 'text-[1.75rem]' :
        size === 'xl' ? 'text-4xl' :
        'text-[1.4rem]'
      ]"
      aria-hidden="true"
    ><span class="wordmark__i">ı<i class="wordmark__dot"></i></span>mag<span class="wordmark__i wordmark__i--lit">ı<i class="wordmark__dot"></i></span></span>
  </router-link>
</template>

<script setup lang="ts">
defineProps({
  /**
   * Link destination
   */
  to: {
    type: [String, Object],
    default: '/'
  },
  /**
   * Size variant
   */
  size: {
    type: String,
    default: 'md',
    validator: (value: string) => ['sm', 'md', 'lg', 'xl'].includes(value)
  }
})
</script>

<style scoped>
.wordmark {
  font-family: 'Bricolage Grotesque', 'Hanken Grotesk', ui-sans-serif, system-ui, sans-serif;
  font-weight: 760;
  font-variation-settings: 'opsz' 72;
  letter-spacing: -0.04em;
  white-space: nowrap;
}

/* A dotless i with its dot drawn on, sized and placed in em so it tracks
   every size variant */
.wordmark__i {
  position: relative;
  display: inline-block;
}

.wordmark__dot {
  position: absolute;
  top: 0.035em;
  left: 52%;
  width: 0.205em;
  height: 0.205em;
  border-radius: 50%;
  background: currentColor;
  transform: translateX(-50%);
}

.wordmark__i--lit .wordmark__dot {
  background: linear-gradient(100deg, #ec4a33, #ee8c10);
  box-shadow: 0 0 0.22em 0.02em rgba(255, 120, 80, 0.35);
}

:global(.dark) .wordmark__i--lit .wordmark__dot {
  background: linear-gradient(100deg, #ff6b5a, #ffb547);
  box-shadow: 0 0 0.22em 0.02em rgba(255, 120, 80, 0.55);
}
</style>
