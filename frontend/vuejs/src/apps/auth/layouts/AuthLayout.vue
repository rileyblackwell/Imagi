<!-- Auth layout — the editorial surface, with the form in a hairline panel. -->
<template>
  <DefaultLayout>
    <div class="editorial auth-page min-h-screen relative font-body">
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <div class="relative z-10 flex min-h-screen w-full items-center justify-center px-6 py-16 pt-28 sm:pt-32">
        <div class="w-full max-w-[30rem] auth-rise">
          <div class="auth-panel">
            <div class="text-center">
              <!-- ImagiLogo's root is a block, so it needs an inline-flex
                   wrapper to sit under text-center. -->
              <span class="inline-flex"><ImagiLogo size="lg" to="/" /></span>

              <h1 class="display mt-8 text-3xl sm:text-[2.4rem]">
                {{ route.meta.title }}
              </h1>
              <p class="lede mt-3">
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
</template>

<script setup lang="ts">
import DefaultLayout from '@/shared/layouts/DefaultLayout.vue'
import { useRoute } from 'vue-router'
import { ImagiLogo } from '@/shared/components/molecules'

const route = useRoute()
</script>

<style scoped>
/* A hairline panel rather than a shadowed card — the form still reads as a
   contained task without a floating slab on the paper. */
.auth-panel {
  padding: 2.5rem 2rem;
  border: 1px solid var(--rule);
  border-radius: 1rem;
  background: var(--paper-raised);
}

@media (min-width: 640px) {
  .auth-panel {
    padding: 3rem 2.75rem;
  }
}

.auth-rise {
  animation: auth-rise 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
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
