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
    <!-- Each i is a dotless ı with its dot drawn on, sized and placed in em so
         it tracks every size variant. The last dot is the light: the Spotlight
         gradient with a soft glow. It is the light theme's gradient in both
         themes: the dark pair (#ff6b5a → #ffb547, glow at 0.55) was written as
         `:global(.dark) .wordmark__i--lit .wordmark__dot`, which Vue compiles to
         a bare `.dark` rule, so it never reached the dot. -->
    <span
      class="wordmark font-['Bricolage_Grotesque','Hanken_Grotesk',ui-sans-serif,system-ui,sans-serif] font-[760] [font-variation-settings:'opsz'_72] tracking-[-0.04em] whitespace-nowrap
             leading-none text-ink dark:text-white transition-colors duration-300"
      :class="[
        size === 'sm' ? 'text-lg' :
        size === 'md' ? 'text-[1.4rem]' :
        size === 'lg' ? 'text-[1.75rem]' :
        size === 'xl' ? 'text-4xl' :
        'text-[1.4rem]'
      ]"
      aria-hidden="true"
    ><span class="wordmark__i relative inline-block">ı<i :class="dot" class="bg-current"></i></span>mag<span class="wordmark__i wordmark__i--lit relative inline-block">ı<i
      :class="dot"
      class="bg-transparent bg-[linear-gradient(100deg,#ec4a33,#ee8c10)] [box-shadow:0_0_0.22em_0.02em_rgba(255,120,80,0.35)]"
    ></i></span></span>
  </router-link>
</template>

<script setup lang="ts">
const dot = 'wordmark__dot absolute top-[0.035em] left-[52%] w-[0.205em] h-[0.205em] rounded-[50%] -translate-x-1/2'

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
