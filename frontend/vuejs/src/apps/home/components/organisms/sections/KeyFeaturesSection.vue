<!-- Key Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12 bg-white dark:bg-[#0a0a0a] transition-colors duration-500">
    <div class="max-w-6xl mx-auto">
      
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">Key Features</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Built for everyone
        </h2>
        <p class="text-xl text-gray-500 dark:text-white/60 max-w-2xl mx-auto transition-colors duration-300">
          Everything you need to turn ideas into working web applications, without the complexity.
        </p>
      </div>

      <!-- Features grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-10">
        
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="group relative"
        >
          <!-- Card -->
          <div class="h-full p-8 rounded-3xl bg-white dark:bg-white/[0.02] border border-gray-200 dark:border-white/10 transition-all duration-300 hover:border-gray-300 dark:hover:border-white/20 hover:scale-[1.02]">
            
            <!-- Icon -->
            <div class="mb-6 flex justify-start">
              <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gray-100 dark:bg-white/[0.05] border border-gray-200 dark:border-white/10 transition-all duration-300 group-hover:scale-110">
                <i :class="[feature.icon, 'text-2xl text-gray-700 dark:text-white/70 transition-colors duration-300']"></i>
              </div>
            </div>
            
            <!-- Content -->
            <h3 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 transition-colors duration-300">
              {{ feature.title }}
            </h3>
            <p class="text-gray-500 dark:text-white/60 leading-relaxed mb-6 transition-colors duration-300">
              {{ feature.description }}
            </p>

            <!-- Feature highlights -->
            <ul class="space-y-3">
              <li 
                v-for="(highlight, hIndex) in feature.highlights" 
                :key="hIndex"
                class="flex items-start gap-3"
              >
                <div class="flex-shrink-0 mt-1">
                  <div class="w-5 h-5 rounded-full bg-gray-100 dark:bg-white/[0.05] flex items-center justify-center">
                    <i class="fas fa-check text-[10px] text-gray-700 dark:text-white/70"></i>
                  </div>
                </div>
                <span class="text-gray-600 dark:text-white/50 text-sm">{{ highlight }}</span>
              </li>
            </ul>

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
