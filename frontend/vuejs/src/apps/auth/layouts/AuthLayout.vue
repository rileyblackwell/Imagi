<!-- Auth layout — the editorial surface, in the home page's header pattern:
     the headline and lede on the left, the form in a hairline panel opposite.
     Stacks on small screens. -->
<template>
  <DefaultLayout minimal-nav>
    <div class="editorial auth-page min-h-screen relative font-body">
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <div class="relative z-10 section-shell pt-28 sm:pt-36 md:pt-40 pb-20 md:pb-28">
        <div class="grid gap-12 md:grid-cols-[minmax(0,1fr)_minmax(0,27rem)] lg:gap-20 md:items-start">
          <div class="auth-rise md:pt-4">
            <p class="eyebrow">
              <span class="eyebrow__rule" aria-hidden="true"></span>
              <span>Imagi</span>
            </p>
            <h1 class="display mt-7 text-[2.6rem] sm:text-5xl md:text-[3.5rem]">
              {{ route.meta.title }}
            </h1>
            <p class="lede mt-6 text-lg max-w-sm">
              {{ route.meta.subtitle }}
            </p>
          </div>

          <div class="auth-panel auth-rise" style="animation-delay: 90ms">
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
</template>

<script setup lang="ts">
import DefaultLayout from '@/shared/layouts/DefaultLayout.vue'
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
/* A hairline panel rather than a shadowed card — the form still reads as a
   contained task without a floating slab on the paper. */
.auth-panel {
  padding: 2rem 1.5rem;
  border: 1px solid var(--rule);
  border-radius: 1rem;
  background: var(--paper-raised);
}

@media (min-width: 640px) {
  .auth-panel {
    padding: 2.5rem 2.25rem;
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
