<template>
  <div class="bg-dark-800 rounded-lg shadow-lg overflow-hidden">
    <!-- Card Header -->
    <div class="px-6 py-4 flex items-center justify-between border-b border-dark-700" v-if="title">
      <h3 class="text-lg font-semibold text-white">{{ title }}</h3>
      <router-link
        v-if="showViewAll && viewAllLink"
        :to="viewAllLink"
        class="text-sm text-primary-400 hover:text-primary-300 transition-colors"
      >
        View All
      </router-link>
    </div>

    <!-- Card Content -->
    <div :class="contentClass">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    default: ''
  },
  showViewAll: {
    type: Boolean,
    default: false
  },
  viewAllLink: {
    type: String,
    default: ''
  },
  contentClass: {
    type: String,
    default: 'p-6'
  }
})
</script>
