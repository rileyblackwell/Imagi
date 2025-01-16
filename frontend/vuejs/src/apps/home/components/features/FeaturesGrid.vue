<!-- Features grid component -->
<template>
  <section class="py-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Section header -->
      <div class="text-center">
        <h2 class="text-3xl font-bold text-white">{{ title }}</h2>
        <p v-if="description" class="mt-4 text-xl text-gray-300 max-w-2xl mx-auto">
          {{ description }}
        </p>
      </div>

      <!-- Features grid -->
      <div class="mt-20 grid grid-cols-1 gap-12 sm:grid-cols-2 lg:grid-cols-3">
        <slot></slot>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'FeaturesGrid',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    columns: {
      type: Number,
      default: 3,
      validator: value => [1, 2, 3, 4].includes(value)
    }
  },
  computed: {
    gridClass() {
      return {
        'sm:grid-cols-2': this.columns >= 2,
        'lg:grid-cols-3': this.columns >= 3,
        'xl:grid-cols-4': this.columns === 4
      }
    }
  }
}
</script> 