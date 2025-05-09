<template>
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <ResourceCard v-for="resource in resources" :key="resource.title" :icon="resource.icon" :title="resource.title" :description="resource.description" />
  </div>
</template>

<script setup lang="ts">
import ResourceCard from '@/shared/components/molecules/ResourceCard.vue'

interface Resource {
  icon: string;
  title: string;
  description: string;
}

const props = defineProps<{ resources: Resource[] }>()
</script>
