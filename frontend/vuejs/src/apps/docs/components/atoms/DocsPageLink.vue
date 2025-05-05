<template>
  <component 
    :is="isExternalLink ? 'a' : 'router-link'" 
    :to="isExternalLink ? undefined : to"
    :href="isExternalLink ? to : undefined"
    :target="isExternalLink ? '_blank' : undefined"
    :rel="isExternalLink ? 'noopener noreferrer' : undefined"
    class="inline-flex items-center text-primary-400 hover:text-primary-300 font-medium transition-colors"
  >
    <slot>{{ text }}</slot>
    <i v-if="isExternalLink" class="fas fa-external-link-alt text-xs ml-1"></i>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  to: string;
  text?: string;
}>();

// Determine if this is an external link
const isExternalLink = computed(() => {
  return props.to.startsWith('http://') || 
         props.to.startsWith('https://') || 
         props.to.startsWith('//');
});
</script> 