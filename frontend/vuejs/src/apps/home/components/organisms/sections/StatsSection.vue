<!-- Stats Section Component -->
<template>
  <section class="py-20 relative overflow-hidden">
    <div class="container mx-auto px-4">
      <!-- Section Header -->
      <SectionHeader
        :title="title"
        :subtitle="subtitle"
      />
      
      <!-- Stats Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mt-12">
        <StatCard
          v-for="(stat, index) in stats"
          :key="index"
          :icon="stat.icon"
          :secondary-icon="stat.secondaryIcon"
          :value="stat.value"
          :label="stat.label"
          :percent="stat.percent"
          :color="stat.color"
          :is-clock="stat.isClock"
        />
      </div>
      
      <!-- Rainbow Gradient Decorative Line -->
      <div class="w-full h-px mt-24 bg-gradient-to-r from-primary-500/0 via-primary-500/50 to-primary-500/0 overflow-hidden relative">
        <div class="absolute inset-0 bg-gradient-to-r from-primary-500/0 via-indigo-500/50 to-primary-500/0 animate-pulse"></div>
      </div>
    </div>
  </section>
</template>

<script>
import { defineComponent, ref } from 'vue'
import StatCard from '@/apps/home/components/molecules/cards/StatCard.vue'
import SectionHeader from '@/apps/home/components/molecules/containers/SectionHeader.vue'

export default defineComponent({
  name: 'StatsSection',
  components: {
    StatCard,
    SectionHeader
  },
  setup() {
    const title = ref('Our Impact')
    const subtitle = ref('Imagi is revolutionizing web development for businesses and developers.')
    
    const stats = ref([
      {
        icon: 'fas fa-users',
        secondaryIcon: 'fas fa-user-group',
        value: '5K+',
        label: 'Active Users',
        percent: null,
        color: 'primary'
      },
      {
        icon: 'fas fa-code',
        secondaryIcon: 'fas fa-laptop-code',
        value: '10K+',
        label: 'Apps Created',
        percent: null,
        color: 'indigo'
      },
      {
        icon: 'fas fa-clock',
        value: '80%',
        label: 'Dev Time Saved',
        percent: 80,
        color: 'green'
      },
      {
        icon: 'fas fa-headset',
        value: '24/7',
        label: 'AI Support',
        percent: 100,
        isClock: true,
        color: 'purple'
      }
    ])
    
    return {
      title,
      subtitle,
      stats
    }
  }
})
</script> 