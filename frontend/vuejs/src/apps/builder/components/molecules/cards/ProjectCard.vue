<template>
  <div class="group relative">
    <!-- Hover effect border -->
    <div class="absolute -inset-[1px] rounded-xl bg-gradient-to-r from-primary-500/30 via-violet-500/30 to-indigo-500/30 opacity-0 group-hover:opacity-100 blur transition duration-300"></div>
    
    <!-- Card content -->
    <div class="relative bg-dark-800/50 backdrop-blur-sm rounded-xl p-6 border border-dark-700 hover:border-primary-500/30 transition-all duration-300">
      <div class="flex items-center justify-between">
        <!-- Project info -->
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-2">
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/10 to-violet-500/10 flex items-center justify-center">
              <i class="fas fa-cube text-primary-400"></i>
            </div>
            <h3 class="text-lg font-semibold text-white truncate">{{ project.name }}</h3>
          </div>
          <div class="flex items-center gap-4 text-sm text-gray-400">
            <span class="flex items-center gap-2">
              <i class="fas fa-clock text-xs"></i>
              {{ formatDate(project.updated_at) }}
            </span>
            <span class="flex items-center gap-2">
              <i class="fas fa-code-branch text-xs"></i>
              v{{ project.version || '1.0' }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2">
          <router-link
            :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
            class="p-2 text-primary-400 hover:text-primary-300 transition-colors rounded-lg hover:bg-primary-500/10"
            title="Open project"
          >
            <i class="fas fa-arrow-right"></i>
          </router-link>
          <button
            @click.stop="confirmDelete"
            class="p-2 text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all duration-200 rounded-lg hover:bg-red-500/10"
            title="Delete project"
          >
            <i class="fas fa-trash"></i>
          </button>
        </div>
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

const emit = defineEmits(['delete']);

function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}

function confirmDelete() {
  emit('delete', props.project);
}
</script>
