<!-- How It Works Section Component -->
<template>
  <section id="how-it-works" class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 bg-dark-950/50 relative">
    <div class="max-w-7xl mx-auto">
      <SectionHeader
        :title="title"
        :subtitle="subtitle"
      />

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 relative">
        <!-- Connected steps with gradient line -->
        <div class="absolute top-14 left-[calc(12.5%-1px)] right-[calc(12.5%-1px)] h-px bg-gradient-to-r from-primary-500/30 via-violet-500/30 to-fuchsia-500/30 hidden lg:block"></div>
        
        <StepCard 
          v-for="(step, index) in steps" 
          :key="index"
          :step-number="index + 1"
          :title="step.title"
          :description="step.description"
          :icon="step.icon"
          :color="step.color"
        />
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent } from 'vue'
import SectionHeader from '@/apps/home/components/molecules/containers/SectionHeader.vue'
import StepCard from '@/apps/home/components/molecules/cards/StepCard.vue'

export default defineComponent({
  name: 'HowItWorksSection',
  components: {
    SectionHeader,
    StepCard
  },
  props: {
    title: {
      type: String,
      default: 'How It Works'
    },
    subtitle: {
      type: String,
      default: 'Follow these simple steps to create your web application'
    },
    steps: {
      type: Array,
      default: () => [
        {
          title: 'Describe Your Vision',
          description: 'Tell us what you want to build using natural language. Describe your features, design preferences, and requirements.',
          icon: 'fas fa-pencil-alt',
          color: 'primary'
        },
        {
          title: 'AI Generation',
          description: 'Our advanced AI analyzes your description and generates all necessary code, from frontend interfaces to backend logic.',
          icon: 'fas fa-magic',
          color: 'indigo'
        },
        {
          title: 'Customize & Refine',
          description: 'Review the generated application, make adjustments, and refine details using natural language commands.',
          icon: 'fas fa-sliders-h',
          color: 'violet'
        },
        {
          title: 'Launch & Scale',
          description: "Deploy your application with confidence, knowing it's built with scalable, secure, and maintainable code.",
          icon: 'fas fa-rocket',
          color: 'fuchsia'
        }
      ]
    }
  }
})
</script> 