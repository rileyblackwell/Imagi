<template>
  <div class="bg-dark-800/50 backdrop-blur-sm rounded-xl border border-dark-700/50">
    <!-- Card Header -->
    <div class="px-6 py-4 border-b border-dark-700/50">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
        <router-link
          v-if="showViewAll && viewAllLink"
          :to="viewAllLink"
          class="text-sm text-primary-400 hover:text-primary-300 transition-colors flex items-center"
        >
          View all
          <i class="fas fa-arrow-right ml-2 text-xs"></i>
        </router-link>
      </div>
    </div>

    <!-- Card Content -->
    <div class="p-6">
      <slot></slot>
    </div>

    <!-- Optional Footer -->
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-dark-700/50">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardContainer',
  props: {
    title: {
      type: String,
      required: true
    },
    showViewAll: {
      type: Boolean,
      default: false
    },
    viewAllLink: {
      type: [String, Object],
      default: null
    }
  }
}
</script>
