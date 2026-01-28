<!-- Features Section - Clean Apple/Cursor-inspired design -->
<template>
  <section class="py-24 md:py-32 px-6 sm:px-8 lg:px-12">
    <div class="max-w-6xl mx-auto">
      
      <!-- Section header -->
      <div class="text-center mb-16 md:mb-20">
        <p class="text-sm font-medium text-gray-500 dark:text-white/50 uppercase tracking-widest mb-4 transition-colors duration-300">Features</p>
        <h2 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight transition-colors duration-300">
          Everything you need
        </h2>
        <p class="text-xl text-gray-500 dark:text-white/60 max-w-2xl mx-auto transition-colors duration-300">
          Build production-ready applications with modern frontends and robust backends.
        </p>
      </div>

      <!-- Features grid - uniform layout -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 lg:gap-10">
        
        <div 
          v-for="(feature, index) in features" 
          :key="index"
          class="group relative text-center"
        >
          <!-- Icon -->
          <div class="mb-6 flex justify-center">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-white dark:bg-white/[0.02] border border-gray-200 dark:border-white/10 transition-all duration-300 group-hover:border-gray-300 dark:group-hover:border-white/20 group-hover:scale-110">
              <i :class="[feature.icon, 'text-2xl text-gray-700 dark:text-white/70 transition-colors duration-300']"></i>
            </div>
          </div>
          
          <!-- Content -->
          <h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-3 transition-colors duration-300">
            {{ feature.title }}
          </h3>
          <p class="text-gray-500 dark:text-white/60 leading-relaxed transition-colors duration-300">
            {{ feature.description }}
          </p>
        </div>

      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'

export default defineComponent({
  name: 'FeaturesSection',
  props: {
    features: {
      type: Array,
      default: () => [
        {
          title: 'AI-Powered Generation',
          description: 'Describe your app in plain English and watch as Imagi generates a complete full-stack application in minutes.',
          icon: 'fas fa-wand-magic-sparkles'
        },
        {
          title: 'Full-Stack Applications',
          description: 'Get both a modern Vue.js frontend and a robust Django REST backend with database models, all working together.',
          icon: 'fas fa-layer-group'
        },
        {
          title: 'No Code Required',
          description: 'Build professional web applications without writing a single line of code. Perfect for non-technical founders.',
          icon: 'fas fa-rocket'
        },
        {
          title: 'Conversational Editing',
          description: 'Refine your app through natural conversation. Chat with AI to add features, fix bugs, or redesign components.',
          icon: 'fas fa-comments'
        },
        {
          title: 'Simple Pricing',
          description: 'Pay only for what you build. No monthly subscriptions, no hidden fees. Credits never expire.',
          icon: 'fas fa-tag'
        },
        {
          title: 'Export Your Code',
          description: 'Download the complete source code anytime. Host it yourself or modify it however you want — it\'s yours.',
          icon: 'fas fa-code'
        }
      ]
    }
  }
})
</script>
