<template>
  <div class="fixed bottom-4 right-4 z-50">
    <button
      @click="isOpen = !isOpen"
      class="p-2 bg-dark-800 hover:bg-dark-700 rounded-lg text-white transition-colors"
      title="Keyboard Shortcuts"
    >
      <span class="sr-only">Keyboard Shortcuts</span>
      <svg
        class="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
        />
      </svg>
    </button>

    <div
      v-if="isOpen"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center"
      @click.self="isOpen = false"
    >
      <div class="bg-dark-800 p-6 rounded-lg max-w-lg w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold text-white">Keyboard Shortcuts</h2>
          <button
            @click="isOpen = false"
            class="text-gray-400 hover:text-white transition-colors"
          >
            <span class="sr-only">Close</span>
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div v-for="(section, index) in shortcuts" :key="index">
            <h3 class="text-white font-medium mb-2">{{ section.title }}</h3>
            <div class="space-y-2">
              <div
                v-for="(shortcut, idx) in section.items"
                :key="idx"
                class="flex justify-between text-sm"
              >
                <span class="text-gray-400">{{ shortcut.description }}</span>
                <kbd class="px-2 py-1 bg-dark-700 rounded text-white">
                  {{ shortcut.keys }}
                </kbd>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isOpen = ref(false)

const shortcuts = [
  {
    title: 'Navigation',
    items: [
      { description: 'Toggle Sidebar', keys: '⌘ + B' },
      { description: 'Quick Search', keys: '⌘ + K' },
      { description: 'Go to Home', keys: '⌘ + H' }
    ]
  },
  {
    title: 'Editor',
    items: [
      { description: 'Save Changes', keys: '⌘ + S' },
      { description: 'Undo', keys: '⌘ + Z' },
      { description: 'Redo', keys: '⌘ + ⇧ + Z' }
    ]
  }
]
</script> 