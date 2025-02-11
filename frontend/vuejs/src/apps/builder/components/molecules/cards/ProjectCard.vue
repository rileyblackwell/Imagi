<template>
  <div class="group bg-dark-900/50 backdrop-blur-sm rounded-xl p-4 border border-dark-700 hover:border-primary-500/50 transition-all duration-200">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-white font-medium mb-1">{{ project.name }}</h3>
        <p class="text-sm text-gray-400">Last modified: {{ formatDate(project.updated_at) }}</p>
      </div>
      <div class="flex items-center space-x-3">
        <router-link
          :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
          class="p-2 text-primary-400 hover:text-primary-300 transition-colors"
          title="Open project"
        >
          <i class="fas fa-arrow-right"></i>
        </router-link>
        <button
          @click="$emit('delete', project)"
          class="p-2 text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all duration-200"
          title="Delete project"
        >
          <i class="fas fa-trash"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  project: {
    type: Object,
    required: true
  }
});

defineEmits(['delete']);

function formatDate(date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
</script>
