<template>
  <div class="bg-dark-800 rounded-lg p-6">
    <form @submit.prevent="$emit('submit')" class="space-y-6">
      <!-- Project Name -->
      <div>
        <label for="name" class="block text-sm font-medium text-gray-200">
          Project Name
        </label>
        <input
          id="name"
          v-model="localName"
          type="text"
          required
          placeholder="My Awesome Project"
          class="mt-1 block w-full rounded-md bg-dark-700 border-dark-600 text-white placeholder-gray-400 focus:border-primary-500 focus:ring-primary-500"
        />
      </div>

      <!-- Project Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-gray-200">
          Description
        </label>
        <textarea
          id="description"
          v-model="localDescription"
          rows="3"
          placeholder="Describe your project..."
          class="mt-1 block w-full rounded-md bg-dark-700 border-dark-600 text-white placeholder-gray-400 focus:border-primary-500 focus:ring-primary-500"
        ></textarea>
      </div>

      <!-- Submit Button -->
      <div class="flex justify-end space-x-4">
        <IconButton
          type="button"
          variant="secondary"
          @click="$emit('cancel')"
        >
          Cancel
        </IconButton>
        <IconButton
          type="submit"
          variant="primary"
          :loading="loading"
        >
          Create Project
        </IconButton>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { IconButton } from '@/shared/components/atoms'

const props = defineProps<{
  name: string
  description: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:name', value: string): void
  (e: 'update:description', value: string): void
  (e: 'submit'): void
  (e: 'cancel'): void
}>()

const localName = computed({
  get: () => props.name,
  set: (value) => emit('update:name', value)
})

const localDescription = computed({
  get: () => props.description,
  set: (value) => emit('update:description', value)
})
</script>
