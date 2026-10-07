<!-- Auth layout — the Spotlight stage, with the form in one centered card
     standing in the light. -->
<template>
  <div class="spotlight auth-root">
  <DefaultLayout minimal-nav>
    <div class="editorial auth-page min-h-screen relative isolate overflow-hidden">
      <div class="sl-spot auth-spot" aria-hidden="true"></div>
      <div class="sl-dots" aria-hidden="true"></div>

      <div class="relative z-10 flex min-h-screen w-full items-center justify-center px-6 py-16 pt-28 sm:pt-32">
        <div class="w-full max-w-[30rem] auth-rise">
          <div class="auth-panel">
            <div class="text-center">
              <!-- ImagiLogo's root is a block, so it needs an inline-flex
                   wrapper to sit under text-center. -->
              <span class="inline-flex"><ImagiLogo size="lg" to="/" /></span>

              <h1 class="sl-display auth-title">
                {{ route.meta.title }}
              </h1>
              <p class="sl-lede auth-lede">
                {{ route.meta.subtitle }}
              </p>
            </div>

            <div class="section-rule my-9" aria-hidden="true"></div>

            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
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
/* The light sits over the card rather than the top edge of the page */
.auth-page .auth-spot {
  background:
    radial-gradient(ellipse 42% 50% at 50% 12%, var(--sl-spot-core) 0%, var(--sl-spot-mid) 45%, transparent 75%),
    radial-gradient(ellipse 80% 60% at 50% -10%, var(--sl-spot-wide), transparent 65%);
}

.auth-title {
  margin-top: 1.75rem;
  font-size: clamp(32px, 4.4vw, 42px);
  line-height: 1.02;
  letter-spacing: -0.03em;
}

.auth-lede {
  margin: 0.75rem auto 0;
  font-size: 16px;
}

/* One card in the light, edged with the same glowing gradient as the home
   page's prompt bar. */
.auth-panel {
  position: relative;
  padding: 2.5rem 2rem;
  border: 1px solid transparent;
  border-radius: 22px;
  background:
    var(--sl-prompt-bg) padding-box,
    var(--sl-prompt-edge) border-box;
  box-shadow: var(--sl-prompt-shadow);
}

/* The form controls take the stage's colours. Their Tailwind classes are
   shared with the signed-in app, so they are re-lit here rather than at the
   source. */
.auth-panel :deep(input:not([type='checkbox'])) {
  border-color: var(--sl-line-strong);
  border-radius: 14px;
  background: var(--sl-chip-bg);
  color: var(--sl-text);
  font-family: var(--sl-font-body);
}

.auth-panel :deep(input:not([type='checkbox'])::placeholder) {
  color: var(--sl-faint);
}

.auth-panel :deep(input:not([type='checkbox']):hover) {
  border-color: color-mix(in srgb, var(--sl-text) 28%, transparent);
}

.auth-panel :deep(input:not([type='checkbox']):focus) {
  border-color: var(--sl-focus);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--sl-amber) 16%, transparent);
}

.auth-panel :deep(.group > span > i),
.auth-panel :deep(label > span > i),
.auth-panel :deep(input ~ button) {
  color: var(--sl-faint);
}

.auth-panel :deep(input ~ button:hover) {
  color: var(--sl-text);
}

.auth-panel :deep(input[type='checkbox']) {
  accent-color: var(--sl-coral);
}

.auth-panel :deep(.ml-3 > label) {
  color: var(--sl-muted);
}

.auth-panel :deep(.ml-3 a) {
  color: var(--sl-text);
  border-color: var(--sl-line-strong);
}

.auth-panel :deep(.ml-3 a:hover) {
  border-color: var(--sl-focus);
}

.auth-panel :deep(.bg-paper\/80) {
  border-color: var(--sl-line);
  background: var(--sl-chip-bg);
}

@media (min-width: 640px) {
  .auth-panel {
    padding: 3rem 2.75rem;
  }
}

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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
