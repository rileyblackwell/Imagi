<!-- Key Features Section (Step 2 - Run) - warm porcelain editorial design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 transition-colors duration-500">

    <!-- Cool baby-blue wash behind the section -->
    <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
      <div class="section-wash-cool absolute -top-24 right-[-15%] w-[760px] h-[560px]"></div>
    </div>

    <div class="relative max-w-6xl mx-auto">

      <!-- Hairline divider -->
      <div class="section-divider mb-20 md:mb-24" aria-hidden="true"></div>

      <!-- Editorial header: headline left, supporting copy right -->
      <div v-reveal class="md:flex md:items-end md:justify-between gap-12 mb-14 md:mb-16">
        <div class="max-w-xl">
          <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-6 transition-colors duration-300">Step 2 &middot; Run</p>
          <h2 class="font-display text-4xl sm:text-5xl md:text-[3.4rem] font-semibold text-blue-950 dark:text-white tracking-[-0.015em] leading-[1.08] text-balance transition-colors duration-300">
            Run your <em class="section-accent-warm not-italic">business</em>
          </h2>
        </div>
        <p class="mt-6 md:mt-0 md:max-w-sm md:pb-2 text-lg text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300">
          Once your app is live, grow it with built-in tools for marketing, sales, and finance&mdash;all in one place.
        </p>
      </div>

      <!-- Features grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div
          v-for="(feature, index) in features"
          :key="index"
          v-reveal="{ delay: 90 + index * 90 }"
          class="lift-card group relative h-full p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] border backdrop-blur-sm transition-all duration-300"
          :class="index % 2 === 1 ? 'border-blue-200/70 dark:border-blue-300/[0.14]' : 'border-orange-200/70 dark:border-orange-300/[0.14]'"
        >
          <!-- Icon -->
          <div
            class="icon-tile relative flex items-center justify-center w-12 h-12 rounded-xl mb-6 ring-1 transition-all duration-300"
            :class="index % 2 === 1 ? 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-900/[0.08] dark:ring-blue-300/[0.18]' : 'bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-900/[0.08] dark:ring-orange-300/[0.18]'"
          >
            <i :class="[feature.icon, 'text-lg', index % 2 === 1 ? 'text-blue-600 dark:text-blue-300' : 'text-orange-600 dark:text-orange-300']"></i>
          </div>

          <!-- Title -->
          <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-3">
            {{ feature.title }}
          </h3>

          <!-- Description -->
          <p class="relative text-blue-950/65 dark:text-blue-100/65 leading-relaxed text-pretty transition-colors duration-300 mb-6">
            {{ feature.description }}
          </p>

          <!-- Highlights checklist -->
          <ul class="relative space-y-2.5 pt-5 border-t border-blue-950/[0.06] dark:border-white/[0.07]">
            <li
              v-for="(highlight, hIndex) in feature.highlights"
              :key="hIndex"
              class="flex items-center gap-2.5"
            >
              <span
                class="flex-shrink-0 w-[18px] h-[18px] rounded-full ring-1 flex items-center justify-center transition-all duration-300"
                :class="index % 2 === 1 ? 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-200/80 dark:ring-blue-300/[0.18]' : 'bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-200/80 dark:ring-orange-300/[0.18]'"
              >
                <i class="fas fa-check text-[9px]" :class="index % 2 === 1 ? 'text-blue-600 dark:text-blue-300' : 'text-orange-600 dark:text-orange-300'"></i>
              </span>
              <span class="text-sm text-blue-950/70 dark:text-blue-100/70 leading-relaxed transition-colors duration-300">{{ highlight }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import reveal from '@/apps/home/directives/reveal'

export default defineComponent({
  name: 'KeyFeaturesSection',
  directives: { reveal },
  props: {
    features: {
      type: Array,
      default: () => [
        {
          title: 'Marketing',
          description: 'Reach customers and grow your audience. Launch campaigns, build a presence, and drive traffic to your app—no marketing team required.',
          icon: 'fas fa-bullhorn',
          highlights: [
            'Email & social campaigns',
            'Landing pages & SEO',
            'Audience insights'
          ]
        },
        {
          title: 'Sales',
          description: 'Turn visitors into paying customers. Manage leads, track your pipeline, and close deals with tools built right into your business.',
          icon: 'fas fa-handshake',
          highlights: [
            'Lead & contact management',
            'Pipeline tracking',
            'Payments & checkout'
          ]
        },
        {
          title: 'Finance',
          description: 'Stay on top of the numbers. Track revenue and expenses, send invoices, and understand the health of your business at a glance.',
          icon: 'fas fa-chart-line',
          highlights: [
            'Revenue & expense tracking',
            'Invoicing & billing',
            'Financial dashboards'
          ]
        }
      ]
    }
  }
})
</script>

<style scoped>
/* Hairline gradient divider that fades at the edges */
.section-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(23, 37, 84, 0.12), transparent);
}

.dark .section-divider {
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
}

/* Soft cool wash */
.section-wash-cool {
  background: radial-gradient(closest-side, rgba(158, 205, 243, 0.2), rgba(158, 205, 243, 0.06) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .section-wash-cool {
  background: radial-gradient(closest-side, rgba(96, 165, 250, 0.08), rgba(96, 165, 250, 0.02) 55%, transparent 75%);
}

/* Italic serif accent in warm ink */
.section-accent-warm {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.05em;
}

.dark .section-accent-warm {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Cards that lift gently on hover */
.lift-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.lift-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.1),
    0 24px 44px -12px rgba(15, 23, 42, 0.14);
}

.dark .lift-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

.dark .lift-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.5),
    0 12px 24px -4px rgba(0, 0, 0, 0.5),
    0 28px 48px -12px rgba(0, 0, 0, 0.6);
}

/* Icon tile nudge on card hover */
.lift-card:hover .icon-tile {
  transform: scale(1.06) rotate(-3deg);
}
</style>
