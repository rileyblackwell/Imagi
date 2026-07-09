<!-- Key Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-blue-50 dark:bg-blue-400/[0.16] border-t border-blue-200/60 dark:border-blue-500/[0.12] transition-colors duration-500 overflow-hidden">

    <div class="relative max-w-6xl mx-auto">

      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/30 bg-orange-50/80 dark:bg-orange-600 text-xs font-semibold text-orange-700 dark:text-white uppercase tracking-[0.18em] mb-5 transition-colors duration-300">Key Features</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-blue-950 dark:text-white mb-6 tracking-tight text-balance transition-colors duration-300">
          Built for everyone
        </h2>
        <p class="text-xl text-blue-950/70 dark:text-blue-100/70 leading-relaxed text-pretty max-w-2xl mx-auto transition-colors duration-300">
          Everything you need to turn ideas into working web applications, without the complexity.
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
            :class="index % 2 === 1 ? 'bg-white border-blue-200/70' : 'bg-white border-orange-200/70'"
          >

            <!-- Title -->
            <h3 class="relative text-xl font-semibold tracking-tight text-blue-950 transition-colors duration-300 mb-4 text-center">
              {{ feature.title }}
            </h3>

            <!-- Description -->
            <p class="relative text-blue-950/70 leading-relaxed text-pretty mb-6 transition-colors duration-300 text-center">
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
                      :class="index % 2 === 1 ? 'bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] ring-blue-200/80' : 'bg-orange-100 ring-orange-200/80'"
                    >
                      <i class="fas fa-check text-[10px]" :class="index % 2 === 1 ? 'text-blue-600' : 'text-orange-600'"></i>
                    </div>
                  </div>
                  <span class="text-blue-950/70 text-sm leading-relaxed transition-colors duration-300">{{ highlight }}</span>
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
          title: 'User-Friendly Interface',
          description: 'Built for non-technical users. No coding knowledge required—just describe what you want and watch it come to life.',
          icon: 'fas fa-user-check',
          highlights: [
            'Intuitive visual builder',
            'Plain English instructions',
            'No technical jargon'
          ]
        },
        {
          title: 'AI-Powered Agent',
          description: 'An intelligent assistant that understands your vision and helps build your application collaboratively through conversation.',
          icon: 'fas fa-wand-magic-sparkles',
          highlights: [
            'Chat-based development',
            'Instant code generation',
            'Smart suggestions'
          ]
        },
        {
          title: 'Managed Deployment',
          description: 'We handle all the technical complexity of deploying your web app. Just click deploy and share your link with the world.',
          icon: 'fas fa-rocket',
          highlights: [
            'One-click deployment',
            'Automatic hosting',
            'SSL & scaling included'
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
</style>
