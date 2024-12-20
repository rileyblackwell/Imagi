<template>
  <div class="builder-page">
    <div class="max-w-7xl mx-auto px-4 py-12">
      <!-- Header Section -->
      <div class="text-center mb-12">
        <h1 class="text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-blue-400 text-transparent bg-clip-text">
          Build Your Web App
        </h1>
        <p class="text-xl text-gray-300 max-w-2xl mx-auto">
          Describe your web application in natural language, and watch as our AI brings your vision to life.
        </p>
      </div>
      
      <!-- Builder Interface -->
      <div class="grid md:grid-cols-2 gap-8">
        <!-- Input Section -->
        <div class="bg-gray-800/50 rounded-xl p-8 border border-gray-700/50">
          <h2 class="text-2xl font-semibold mb-4">Describe Your App</h2>
          <p class="text-gray-300 mb-6">
            Be as detailed as you'd like. Include information about:
            <ul class="list-disc list-inside space-y-2 mt-2">
              <li>Purpose and main features</li>
              <li>Design preferences and style</li>
              <li>User interactions and flow</li>
              <li>Data management needs</li>
            </ul>
          </p>
          <textarea
            v-model="appDescription"
            class="w-full h-64 bg-gray-900 text-white rounded-lg p-4 border border-gray-700 
                   focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 outline-none
                   placeholder-gray-500"
            placeholder="Example: I want to create a task management app with a clean, modern interface. Users should be able to create projects, add tasks, set due dates, and track progress..."
          ></textarea>
          
          <div class="flex justify-between items-center mt-6">
            <button 
              @click="clearDescription"
              class="px-4 py-2 text-gray-400 hover:text-gray-300 transition-colors">
              Clear
            </button>
            <button 
              @click="generateApp"
              class="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg 
                     font-semibold hover:from-cyan-600 hover:to-blue-600 transition-all 
                     transform hover:scale-105 shadow-lg hover:shadow-cyan-500/25 
                     flex items-center gap-2"
              :disabled="!appDescription">
              Generate App
              <i class="fas fa-wand-magic-sparkles" />
            </button>
          </div>
        </div>

        <!-- Preview Section -->
        <div class="bg-gray-800/50 rounded-xl p-8 border border-gray-700/50">
          <h2 class="text-2xl font-semibold mb-4">Preview</h2>
          <p class="text-gray-300 mb-6">
            Your app preview and generated code will appear here.
          </p>
          
          <div v-if="!isGenerating && !preview" class="flex flex-col items-center justify-center h-64 text-gray-500">
            <i class="fas fa-desktop text-4xl mb-4"></i>
            <p>Start by describing your app</p>
          </div>

          <div v-if="isGenerating" class="flex flex-col items-center justify-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mb-4"></div>
            <p class="text-gray-300">Generating your application...</p>
          </div>

          <div v-if="preview" class="h-64 overflow-auto">
            <!-- Preview content will go here -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const appDescription = ref('')
const isGenerating = ref(false)
const preview = ref(null)

const clearDescription = () => {
  appDescription.value = ''
}

const generateApp = async () => {
  if (!appDescription.value) return
  
  isGenerating.value = true
  // TODO: Implement app generation logic
  await new Promise(resolve => setTimeout(resolve, 2000)) // Simulated delay
  isGenerating.value = false
}
</script>

<style>
.builder-page {
  @apply min-h-screen bg-gradient-to-b from-gray-900 to-gray-800;
}

/* Custom scrollbar for textareas */
textarea {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.700') theme('colors.gray.900');
}

textarea::-webkit-scrollbar {
  width: 8px;
}

textarea::-webkit-scrollbar-track {
  @apply bg-gray-900 rounded-r-lg;
}

textarea::-webkit-scrollbar-thumb {
  @apply bg-gray-700 rounded-full;
}

textarea::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-600;
}
</style> 