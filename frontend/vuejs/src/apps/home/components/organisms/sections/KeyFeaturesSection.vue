<!-- Key Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="relative py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-gray-50 dark:bg-[#0d0d0d] transition-colors duration-500 overflow-hidden">

    <!-- Subtle ambient glow -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-0 right-1/4 w-[500px] h-[500px] bg-gradient-radial from-blue-500/[0.05] via-transparent to-transparent rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-gradient-radial from-violet-500/[0.05] via-transparent to-transparent rounded-full blur-3xl"></div>
    </div>

    <div class="relative max-w-6xl mx-auto">

      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <span class="inline-flex items-center gap-2 px-3 py-1 mb-5 rounded-full border border-gray-200/80 dark:border-white/10 bg-white/70 dark:bg-white/[0.04] backdrop-blur-md text-xs font-semibold uppercase tracking-widest text-gray-600 dark:text-white/60 transition-colors duration-300">
          <span class="w-1.5 h-1.5 rounded-full bg-gradient-to-r from-blue-500 to-violet-500"></span>
          Key Features
        </span>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Built for everyone
        </h2>
        <p class="text-xl text-gray-600 dark:text-white/70 max-w-2xl mx-auto transition-colors duration-300">
          Everything you need to turn ideas into working web applications, without the complexity.
        </p>
      </div>

      <!-- Features grid with enhanced cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">

        <div
          v-for="(feature, index) in features"
          :key="index"
          class="sleek-card group relative h-full overflow-hidden p-8 rounded-2xl bg-white dark:bg-white/[0.03] border border-gray-200/80 dark:border-white/10 transition-all duration-300"
        >
          <span class="card-topline"></span>

          <!-- Icon -->
          <div class="relative mb-6">
            <div class="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/10 to-violet-500/10 dark:from-blue-500/20 dark:to-violet-500/20 border border-blue-500/10 dark:border-white/10 transition-all duration-300 group-hover:scale-105">
              <i :class="[feature.icon, 'text-xl text-blue-600 dark:text-blue-300']"></i>
            </div>
          </div>

          <!-- Title -->
          <h3 class="relative text-xl font-semibold text-gray-900 dark:text-white transition-colors duration-300 mb-3">
            {{ feature.title }}
          </h3>

          <!-- Description -->
          <p class="relative text-gray-600 dark:text-white/60 leading-relaxed mb-6 transition-colors duration-300">
            {{ feature.description }}
          </p>

          <!-- Feature highlights with green checkmarks -->
          <ul class="relative space-y-3 pt-5 border-t border-gray-100 dark:border-white/[0.06]">
            <li
              v-for="(highlight, hIndex) in feature.highlights"
              :key="hIndex"
              class="flex items-center gap-3"
            >
              <span class="flex-shrink-0 w-5 h-5 rounded-full bg-emerald-100 dark:bg-emerald-500/15 flex items-center justify-center transition-all duration-300">
                <i class="fas fa-check text-[10px] text-emerald-600 dark:text-emerald-400"></i>
              </span>
              <span class="text-gray-600 dark:text-white/60 text-sm transition-colors duration-300">{{ highlight }}</span>
            </li>
          </ul>

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
/* Crisp, sharply-defined cards: hairline edge + tight layered shadow, with subtle hover lift */
.sleek-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.sleek-card:hover {
  transform: translateY(-4px);
  border-color: rgba(59, 130, 246, 0.25);
  box-shadow:
    0 0 0 1px rgba(59, 130, 246, 0.06),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 10px 20px -4px rgba(15, 23, 42, 0.10),
    0 24px 48px -14px rgba(59, 130, 246, 0.18);
}

.dark .sleek-card {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 8px 24px -12px rgba(0, 0, 0, 0.6);
}

.dark .sleek-card:hover {
  transform: translateY(-4px);
  border-color: rgba(96, 165, 250, 0.3);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 12px 32px -10px rgba(0, 0, 0, 0.7),
    0 0 32px -8px rgba(59, 130, 246, 0.25);
}

/* Gradient accent line that appears along the top edge on hover */
.card-topline {
  position: absolute;
  top: 0;
  left: 1.5rem;
  right: 1.5rem;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.6), rgba(139, 92, 246, 0.6), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.sleek-card:hover .card-topline {
  opacity: 1;
}

@media (prefers-reduced-motion: reduce) {
  .sleek-card:hover {
    transform: none;
  }
}
</style>
