<!-- Features section component -->
<template>
  <section class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section header -->
      <div class="text-center">
        <h2 class="text-3xl font-bold">
          <GradientText variant="secondary" size="3xl">{{ title }}</GradientText>
        </h2>
        <p v-if="description" class="mt-4 text-xl text-gray-300 max-w-2xl mx-auto">
          {{ description }}
        </p>
      </div>

      <!-- Features grid -->
      <div class="mt-20">
        <FeaturesGrid :columns="columns">
          <template v-for="feature in features" :key="feature.title">
            <FeatureCard
              :icon="feature.icon"
              :title="feature.title"
              :description="feature.description"
            />
          </template>
        </FeaturesGrid>
      </div>

      <!-- Optional CTA -->
      <div v-if="$slots.cta" class="mt-12 text-center">
        <slot name="cta"></slot>
      </div>
    </div>
  </section>
</template>

<script>
import GradientText from '@/apps/home/components/shared/GradientText.vue'
import FeatureCard from '@/apps/home/components/ui/FeatureCard.vue'
import FeaturesGrid from '@/apps/home/components/ui/FeaturesGrid.vue'

export default {
  name: 'FeaturesSection',
  components: {
    GradientText,
    FeaturesGrid,
    FeatureCard
  },
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    features: {
      type: Array,
      required: true,
      validator: value => value.every(feature => 
        feature.icon && feature.title && feature.description
      )
    },
    columns: {
      type: Number,
      default: 3,
      validator: value => [1, 2, 3, 4].includes(value)
    }
  }
}
</script> 