<!-- Auth Layout - warm porcelain editorial design matching Home page -->
<template>
  <DefaultLayout>
    <!-- Warm porcelain canvas that hands off to the white footer -->
    <div class="auth-page min-h-screen relative overflow-hidden font-body transition-colors duration-500">
      <!-- Grain texture over the whole canvas -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <!-- Atmosphere: soft apricot + baby-blue washes behind the card -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div class="auth-glow-warm absolute -top-32 left-1/2 -translate-x-1/3 w-[820px] h-[520px]"></div>
        <div class="auth-glow-cool absolute top-16 -left-48 w-[640px] h-[480px]"></div>
      </div>

      <!-- Content wrapper with proper spacing -->
      <div class="flex min-h-screen w-full relative z-10">
        <div class="w-full flex items-center justify-center px-4 sm:px-6 py-16 pt-28 sm:pt-32">
          <!-- Auth Container -->
          <div class="w-full max-w-[520px] mx-auto">
            <!-- Porcelain crisp card: hairline border + layered soft shadow -->
            <div class="relative auth-card-rise">
              <div class="crisp-card relative rounded-2xl border border-blue-200/70 dark:border-blue-300/[0.14] bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm overflow-hidden transition-colors duration-300">
                <!-- Card content -->
                <div class="relative z-10 p-8 sm:p-10">
                  <!-- Logo and Title Section -->
                  <div class="text-center mb-10">
                    <div class="inline-flex items-center justify-center mb-8">
                      <ImagiLogo size="xl" to="/" />
                    </div>

                    <!-- Title -->
                    <h2 class="font-display text-3xl sm:text-4xl font-semibold tracking-[-0.02em] mb-3 leading-[1.05] text-balance text-blue-950 dark:text-white transition-colors duration-300">
                      {{ route.meta.title }}
                    </h2>
                    <p class="text-base text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
                      {{ route.meta.subtitle }}
                    </p>
                  </div>

                  <!-- Main Content with transition -->
                  <router-view v-slot="{ Component }">
                    <transition name="fade" mode="out-in">
                      <component :is="Component" />
                    </transition>
                  </router-view>
                </div>
              </div>
            </div>
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
/* Warm porcelain canvas fading to white so it hands off seamlessly
   to the footer (footer is bg-white / dark #0a0a0a) */
.auth-page {
  background: linear-gradient(180deg, #fdf9f2 0%, #faf7f1 45%, #ffffff 100%);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

:root.dark .auth-page,
.dark .auth-page {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0b0f 50%, #0a0a0a 100%);
}

/* Fine film grain keeps the soft gradients from banding and adds texture */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

:root.dark .grain-overlay,
.dark .grain-overlay {
  opacity: 0.05;
  mix-blend-mode: overlay;
}

/* Atmosphere washes behind the card */
.auth-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.16), rgba(251, 146, 60, 0.05) 55%, transparent 75%);
  filter: blur(40px);
}

.auth-glow-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.28), rgba(158, 205, 243, 0.08) 55%, transparent 75%);
  filter: blur(44px);
}

.dark .auth-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.09), rgba(251, 146, 60, 0.025) 55%, transparent 75%);
}

.dark .auth-glow-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.11), rgba(96, 165, 250, 0.03) 55%, transparent 75%);
}

/* Crisp, sharply-defined card: hairline edge + tight layered shadow (matches marketing pages) */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

:root.dark .crisp-card,
.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

/* Fade transition between auth views */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Card rises gently on page load */
.auth-card-rise {
  animation: auth-rise 0.8s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes auth-rise {
  from {
    opacity: 0;
    transform: translateY(22px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .auth-card-rise {
    animation: none;
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>

<!-- Unscoped: brand-tinted text selection on the auth pages -->
<style>
.auth-page ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .auth-page ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style>
