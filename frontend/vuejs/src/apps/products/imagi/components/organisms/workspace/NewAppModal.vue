<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="close" />

    <!-- Modal Panel -->
    <div class="relative w-full max-w-lg mx-4 rounded-2xl border border-white/10 bg-dark-900/90 shadow-2xl ring-1 ring-white/5 overflow-hidden">
      <!-- Header -->
      <div class="px-5 py-4 flex items-center gap-3 border-b border-white/10 bg-dark-900/60">
        <span class="w-8 h-8 rounded-md flex items-center justify-center border bg-white/[0.05] border-white/[0.08] text-white/70">
          <i class="fas fa-cubes"></i>
        </span>
        <div class="flex flex-col">
          <span class="text-sm font-semibold text-white">Create New App</span>
          <span class="text-xxs text-gray-400">Define a short name and optional description.</span>
        </div>
        <button
          type="button"
          class="ml-auto text-gray-400 hover:text-white px-2 py-1 rounded-md hover:bg-white/5"
          @click="close"
          aria-label="Close"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Body -->
      <form @submit.prevent="submit" class="px-5 py-4 space-y-4">
        <!-- Name -->
        <div>
          <label class="block text-xs font-medium text-gray-300 mb-1">App name</label>
          <div class="relative">
            <input
              v-model.trim="name"
              type="text"
              placeholder="e.g. blog"
              class="w-full px-3 py-2 text-sm bg-dark-900/80 border rounded-md text-white placeholder-gray-500 outline-none focus:ring-0"
              :class="validName ? 'border-dark-700/60 focus:border-primary-500/40' : 'border-rose-500/40 focus:border-rose-400/50'"
              :disabled="isSubmitting"
              autofocus
            />
          </div>
          <p v-if="!validName && name.length" class="mt-1 text-xxs text-rose-300">
            Name must start with a letter and contain only lowercase letters and numbers.
          </p>
          <p class="mt-1 text-xxs text-gray-400">This becomes the folder under <code class="text-[10px]">src/apps/</code>.</p>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-xs font-medium text-gray-300 mb-1">Description <span class="text-gray-500">(optional)</span></label>
          <textarea
            v-model.trim="description"
            rows="3"
            placeholder="Short description of what this app contains..."
            class="w-full px-3 py-2 text-sm bg-dark-900/80 border border-dark-700/60 rounded-md text-white placeholder-gray-500 outline-none focus:ring-0 focus:border-primary-500/40 resize-none"
            :disabled="isSubmitting"
          />
        </div>

        <!-- Actions -->
        <div class="pt-2 flex items-center justify-end gap-2 border-t border-white/5">
          <button
            type="button"
            class="text-xs px-3 py-2 rounded-md border border-white/10 text-gray-300 hover:text-white hover:bg-white/5"
            @click="close"
            :disabled="isSubmitting"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="text-xs px-3 py-2 rounded-md border bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 border-white/[0.08] text-white hover:bg-gray-800 disabled:opacity-60 disabled:cursor-not-allowed"
            :disabled="!validName || isSubmitting"
          >
            <span v-if="isSubmitting" class="inline-flex items-center gap-2">
              <i class="fas fa-spinner fa-spin"></i>
              Creating…
            </span>
            <span v-else class="inline-flex items-center gap-2">
              <i class="fas fa-plus"></i>
              Create App
            </span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'

const props = withDefaults(defineProps<{
  modelValue: boolean
  defaultName?: string
  defaultDescription?: string
  submitting?: boolean
}>(), {
  modelValue: false,
  defaultName: '',
  defaultDescription: '',
  submitting: false,
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit', payload: { name: string; description: string }): void
}>()

const name = ref(props.defaultName)
const description = ref(props.defaultDescription)
const isSubmitting = computed(() => props.submitting)

const validName = computed(() => /^[a-z][a-z0-9]*$/.test(name.value || ''))

function close() {
  emit('update:modelValue', false)
}

function submit() {
  if (!validName.value || isSubmitting.value) return
  emit('submit', { name: name.value.trim(), description: description.value.trim() })
}

watch(() => props.modelValue, (open) => {
  if (open) {
    // Reset values when opened
    name.value = props.defaultName || ''
    description.value = props.defaultDescription || ''
  }
})

onMounted(() => {
  // no-op
})
</script>
