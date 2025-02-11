<template>
  <form @submit.prevent="$emit('submit')" class="space-y-6">
    <div class="relative">
      <!-- Label -->
      <label class="block text-sm font-medium text-gray-400 mb-2">Project Name</label>
      
      <!-- Input group -->
      <div class="relative group">
        <div class="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-xl blur opacity-0 group-focus-within:opacity-100 transition duration-300"></div>
        <input
          :value="value"
          @input="$emit('update:value', $event.target.value)"
          type="text"
          placeholder="Enter your project name"
          class="relative w-full px-4 py-3 bg-dark-900/50 border border-dark-600 focus:border-primary-500/50 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
          required
        >
      </div>
    </div>

    <!-- Submit button -->
    <button
      type="submit"
      :disabled="isLoading || !value.trim()"
      class="relative w-full group"
    >
      <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 to-violet-500 rounded-xl blur opacity-75 group-hover:opacity-100 transition duration-300"></div>
      <div class="relative flex items-center justify-center px-6 py-3 bg-dark-900 rounded-xl transition-all duration-300">
        <i class="fas fa-magic mr-2 text-primary-400 group-hover:text-primary-300"></i>
        <span class="font-medium text-white">
          {{ isLoading ? 'Creating Project...' : 'Create Project' }}
        </span>
      </div>
    </button>
  </form>
</template>

<script setup>
defineProps({
  value: {
    type: String,
    required: true
  },
  isLoading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['update:value', 'submit']);
</script>
