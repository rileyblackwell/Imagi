<!-- Features Section Component -->
<template>
  <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 relative">
    <div class="max-w-7xl mx-auto">
      <SectionHeader
        :title="title"
        :subtitle="subtitle"
      />

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8 relative">
        <!-- Connected cards with thin gradient line -->
        <div class="absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-primary-500/0 via-primary-500/20 to-primary-500/0 -z-10 hidden lg:block"></div>
        
        <FeatureCard 
          v-for="(feature, index) in features" 
          :key="index"
          :title="feature.title"
          :description="feature.description"
          :icon="feature.icon"
          :color="feature.color"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import SectionHeader from '@/apps/home/components/molecules/containers/SectionHeader.vue'
import FeatureCard from '@/apps/home/components/molecules/cards/FeatureCard.vue'

export default defineComponent({
  name: 'FeaturesSection',
  components: {
    SectionHeader,
    FeatureCard
  },
  props: {
    title: {
      type: String,
      default: 'Why Choose Imagi'
    },
    subtitle: {
      type: String,
      default: 'Transform your ideas into reality with powerful AI-driven web development'
    },
    features: {
      type: Array,
      default: () => [
        {
          title: 'Natural Language Input',
          description: 'Describe your vision in plain English, and watch as it transforms into reality.',
          icon: 'fas fa-keyboard',
          color: 'primary'
        },
        {
          title: 'Rapid Development',
          description: 'Build websites and applications in minutes, not months.',
          icon: 'fas fa-bolt',
          color: 'indigo'
        },
        {
          title: 'Professional Code',
          description: 'Generate clean, maintainable code that follows industry best practices.',
          icon: 'fas fa-code',
          color: 'violet'
        }
      ]
    }
  }
})
</script> 