<!-- Key Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-blue-50 dark:bg-[#0e141f] border-t border-blue-200/60 dark:border-blue-400/[0.14] transition-colors duration-500 overflow-hidden">

    <div class="relative max-w-6xl mx-auto">

      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Step 2 · Run</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
          Run your business
        </h2>
        <p class="text-xl text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty max-w-2xl mx-auto transition-colors duration-300">
          Once your app is live, grow it with built-in tools for marketing, sales, and finance—all in one place.
        </p>
      </div>

      <!-- Features grid with enhanced cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <div
          v-for="(feature, index) in features"
          :key="index"
          class="relative"
        >
          <!-- Card with tinted background alternating blue / orange -->
          <div
            class="relative h-full p-8 rounded-2xl border crisp-card transition-colors duration-300"
            :class="index % 2 === 1 ? 'bg-white dark:bg-white/[0.05] border-blue-200/70 dark:border-blue-300/[0.16]' : 'bg-white dark:bg-white/[0.05] border-orange-200/70 dark:border-orange-300/[0.16]'"
          >

            <!-- Title -->
            <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300 mb-4 text-center">
              {{ feature.title }}
            </h3>

            <!-- Description -->
            <p class="relative text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty mb-6 transition-colors duration-300 text-center">
              {{ feature.description }}
            </p>

            <!-- Feature highlights with accent-colored checkmarks -->
            <div class="relative flex justify-center">
              <ul class="space-y-3 inline-flex flex-col">
                <li
                  v-for="(highlight, hIndex) in feature.highlights"
                  :key="hIndex"
                  class="flex items-start gap-3"
                >
                  <div class="flex-shrink-0 mt-0.5">
                    <div
                      class="w-5 h-5 rounded-full ring-1 flex items-center justify-center transition-all duration-300"
                      :class="index % 2 === 1 ? 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-blue-200/80 dark:ring-blue-300/[0.18]' : 'bg-orange-100 dark:bg-orange-400/[0.14] ring-orange-200/80 dark:ring-orange-300/[0.18]'"
                    >
                      <i class="fas fa-check text-[10px]" :class="index % 2 === 1 ? 'text-blue-600 dark:text-blue-300' : 'text-orange-600 dark:text-orange-300'"></i>
                    </div>
                  </div>
                  <span class="text-blue-950/70 dark:text-blue-100/70 text-sm leading-relaxed transition-colors duration-300">{{ highlight }}</span>
                </li>
              </ul>
            </div>

          </div>
        </div>

      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'KeyFeaturesSection',
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
/* Crisp, sharply-defined cards: hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
