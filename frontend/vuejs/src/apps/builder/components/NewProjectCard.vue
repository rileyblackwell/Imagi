<template>
  <div class="p-6 bg-dark-900 rounded-xl border border-dark-700">
    <h3 class="text-xl font-semibold text-white mb-4">Create New Project</h3>
    
    <div class="space-y-4">
      <div class="space-y-2">
        <label for="projectName" class="block text-sm text-gray-400">
          Project Name
        </label>
        <input
          id="projectName"
          type="text"
          :value="modelValue"
          @input="$emit('update:modelValue', $event.target.value)"
          placeholder="Enter project name"
          class="w-full px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder:text-gray-500 focus:border-primary-500 transition-colors"
          :disabled="isLoading"
        />
      </div>
      
      <button
        @click="$emit('submit')"
        :disabled="!modelValue?.trim() || isLoading"
        class="w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <template v-if="isLoading">
          <i class="fas fa-spinner fa-spin mr-2"></i>
          Creating...
        </template>
        <template v-else>
          <i class="fas fa-plus mr-2"></i>
          Create Project
        </template>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['update:modelValue', 'submit']);
</script>
