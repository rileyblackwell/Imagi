<!-- Use Cases Section Component -->
<template>
  <section class="py-12 md:py-24 px-4 sm:px-6 lg:px-8 relative">
    <div class="max-w-7xl mx-auto">
      <SectionHeader
        :title="title"
        :subtitle="subtitle"
      />

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 relative">
        <!-- Connected cards with thin gradient line -->
        <div class="absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-primary-500/0 via-primary-500/20 to-primary-500/0 -z-10 hidden lg:block"></div>
        
        <FeatureCard 
          v-for="(useCase, index) in useCases" 
          :key="index"
          :title="useCase.title"
          :description="useCase.description"
          :icon="useCase.icon"
          :color="useCase.color"
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
  name: 'UseCasesSection',
  components: {
    SectionHeader,
    FeatureCard
  },
  props: {
    title: {
      type: String,
      default: 'What You Can Build'
    },
    subtitle: {
      type: String,
      default: 'Create a wide range of applications for any purpose'
    },
    useCases: {
      type: Array,
      default: () => [
        {
          title: 'E-commerce Sites',
          description: 'Create full-featured online stores with product catalogs, shopping carts, and secure payment processing.',
          icon: 'fas fa-store',
          color: 'primary'
        },
        {
          title: 'Business Applications',
          description: 'Build custom CRM systems, inventory management tools, and other business-specific applications.',
          icon: 'fas fa-briefcase',
          color: 'indigo'
        },
        {
          title: 'Community Platforms',
          description: 'Develop social networks, forums, and community-driven websites with user management and content sharing.',
          icon: 'fas fa-users',
          color: 'violet'
        },
        {
          title: 'Analytics Dashboards',
          description: 'Create data visualization tools and interactive dashboards for business intelligence and reporting.',
          icon: 'fas fa-chart-line',
          color: 'fuchsia'
        }
      ]
    }
  }
})
</script> 