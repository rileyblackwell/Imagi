<!-- Auth layout — the Spotlight stage, with the form in one centered card
     standing in the light. -->
<template>
  <div class="spotlight auth-root">
  <DefaultLayout minimal-nav>
    <div class="editorial auth-page min-h-screen relative isolate overflow-hidden">
      <!-- The light sits over the card rather than the top edge of the page
           (`!` over .sl-spot's own pool) -->
      <div
        class="sl-spot !bg-[radial-gradient(ellipse_42%_50%_at_50%_12%,var(--sl-spot-core)_0%,var(--sl-spot-mid)_45%,transparent_75%),radial-gradient(ellipse_80%_60%_at_50%_-10%,var(--sl-spot-wide),transparent_65%)]"
        aria-hidden="true"
      ></div>
      <div class="sl-dots" aria-hidden="true"></div>

      <div class="relative z-10 flex min-h-screen w-full items-center justify-center px-6 py-16 pt-28 sm:pt-32">
        <div class="w-full max-w-[30rem] auth-rise">
          <!-- One card in the light, edged with the same glowing gradient as
               the home page's prompt bar: the fill on the padding box, the
               edge on the border box. -->
          <div
            class="auth-panel relative py-10 px-8 sm:py-12 sm:px-11 border border-transparent rounded-[22px]
                   [background:var(--sl-prompt-bg)_padding-box,var(--sl-prompt-edge)_border-box] shadow-sl-prompt"
          >
            <div class="text-center">
              <!-- ImagiLogo's root is a block, so it needs an inline-flex
                   wrapper to sit under text-center. -->
              <span class="inline-flex"><ImagiLogo size="lg" to="/" /></span>

              <!-- `!mt-7`: .sl-display zeroes the margin -->
              <h1 class="sl-display !mt-7 text-[clamp(32px,4.4vw,42px)] leading-[1.02] tracking-[-0.03em]">
                {{ route.meta.title }}
              </h1>
              <p class="sl-lede !mt-3 !mx-auto !text-[16px]">
                {{ route.meta.subtitle }}
              </p>
            </div>

            <div class="section-rule my-9" aria-hidden="true"></div>

            <router-view v-slot="{ Component }">
              <transition
                mode="out-in"
                enter-active-class="[transition:opacity_0.2s_ease]"
                leave-active-class="[transition:opacity_0.2s_ease]"
                enter-from-class="opacity-0"
                leave-to-class="opacity-0"
              >
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
  </div>
</template>

<script setup lang="ts">
import DefaultLayout from '@/shared/layouts/DefaultLayout.vue'
import { useRoute } from 'vue-router'
import { ImagiLogo } from '@/shared/components/molecules'

const route = useRoute()
</script>

<style scoped>
/* The form controls take the stage's colours. FormInput and PasswordInput
   carry theirs on their own templates; these three reach into components
   this layout does not own (GradientButton's icon, FormCheckbox's box and
   label), so they stay :deep() rules. */
.auth-panel :deep(button.group > span > i) {
  color: var(--sl-faint);
}

.auth-panel :deep(input[type='checkbox']) {
  accent-color: var(--sl-coral);
}

.auth-panel :deep(.ml-3 > label) {
  color: var(--sl-muted);
}

/* Stays CSS: a utility cannot name a scoped @keyframes */
.auth-rise {
  animation: auth-rise 0.7s var(--app-ease) both;
}

@keyframes auth-rise {
  from {
    opacity: 0;
    transform: translateY(14px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .auth-rise {
    animation: none;
  }
}
</style>
