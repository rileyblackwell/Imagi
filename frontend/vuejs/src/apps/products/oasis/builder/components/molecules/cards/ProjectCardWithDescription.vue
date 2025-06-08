<template>
  <div class="group relative transform transition-all duration-300">
    <div class="relative bg-dark-900/80 backdrop-blur-lg rounded-2xl overflow-hidden h-full flex flex-col border border-dark-800/60 shadow-lg shadow-dark-900/20 transition-all duration-300 hover:translate-y-[-2px]">
      <!-- Card header with gradient -->
      <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-violet-500"></div>
      
      <!-- Subtle glowing orb effect -->
      <div class="absolute -top-20 -right-20 w-40 h-40 rounded-full opacity-5 blur-3xl transition-opacity duration-500 group-hover:opacity-10 bg-violet-500"></div>
      
      <div class="relative z-10 p-6 flex flex-col h-full">
        <!-- Project header -->
        <div class="flex items-center mb-4">
          <div class="flex items-center gap-3 w-full">
            <!-- Modern icon with subtle effect -->
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/15 to-violet-500/15 flex items-center justify-center transition-all duration-300 border border-indigo-500/10 shadow-md">
              <i class="fas fa-cube text-indigo-300 text-base"></i>
            </div>
            
            <!-- Project name with improved typography -->
            <h3 class="text-lg font-semibold text-white truncate">
              {{ project.name }}
            </h3>
          </div>
        </div>
        
        <!-- Description with edit capability -->
        <div class="mb-4 flex-grow">
          <div v-if="editingDescription === project.id" class="relative group/input w-full mb-2">
            <textarea
              :value="editedDescription"
              @input="$emit('update:editedDescription', $event.target.value)"
              placeholder="Project description..."
              class="w-full px-3 py-2 bg-dark-800/60 border border-dark-600 focus:ring-2 focus:ring-indigo-500 focus:border-transparent rounded-lg text-white placeholder-gray-500 focus:outline-none transition-all duration-200 min-h-[80px] resize-y"
              rows="3"
              @keydown.esc="$emit('cancel-edit')"
            ></textarea>
            <div class="flex items-center gap-2 mt-2">
              <button 
                @click="$emit('save-description', project)"
                class="px-3 py-1.5 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-md transition-all duration-200 flex items-center"
              >
                <i class="fas fa-check mr-1.5"></i> Save
              </button>
              <button 
                @click="$emit('cancel-edit')"
                class="px-3 py-1.5 text-xs font-medium bg-dark-800 hover:bg-dark-700 text-gray-400 hover:text-gray-300 rounded-md border border-dark-700 transition-all duration-200 flex items-center"
              >
                <i class="fas fa-times mr-1.5"></i> Cancel
              </button>
            </div>
          </div>
          <div v-else class="w-full">
            <!-- Modern separator -->
            <div class="w-full h-px bg-dark-700/50 mb-3"></div>
            
            <div class="flex flex-col w-full">
              <div class="flex justify-between items-start gap-2">
                <p class="text-gray-300 text-sm flex-grow pr-2 line-clamp-3">
                  {{ project.description || 'No description provided' }}
                </p>
                <button 
                  @click="$emit('start-edit', project)"
                  class="text-indigo-400 hover:text-indigo-300 transition-colors flex-shrink-0 mt-0.5"
                  title="Edit description"
                >
                  <i class="fas fa-edit text-xs"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer section -->
        <div class="mt-auto">
          <div class="flex items-center text-xs text-gray-400 mb-4">
            <i class="fas fa-history text-xs opacity-70 mr-1.5"></i>
            Updated {{ formatDate(project.updated_at) }}
          </div>
          
          <div class="flex items-center gap-2 justify-between">
            <!-- Professional Open project button -->
            <button
              @click="$emit('open', project)"
              class="py-2 px-4 text-white text-xs font-medium transition-all duration-200 rounded-md bg-indigo-600 hover:bg-indigo-500 shadow-sm text-center flex items-center justify-center flex-1"
              title="Open project"
            >
              <i class="fas fa-code mr-1.5"></i>
              Open Project
            </button>
            
            <!-- Sleek Delete button with better styling -->
            <button
              @click="$emit('delete', project)"
              class="p-2 text-gray-400 hover:text-red-400 transition-all duration-200 rounded-md hover:bg-dark-800 border border-dark-700 flex items-center justify-center h-9 w-9"
              title="Delete project"
            >
              <i class="fas fa-trash-alt text-xs"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  project: {
    type: Object,
    required: true
  },
  editingDescription: {
    type: [String, Number],
    default: null
  },
  editedDescription: {
    type: String,
    default: ''
  }
});

const emit = defineEmits([
  'start-edit',
  'save-description', 
  'cancel-edit',
  'delete',
  'open',
  'update:editedDescription'
]);

function formatDate(date) {
  if (!date) return 'Never updated';
  
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}
</script>

<style scoped>
/* Line clamp for description */
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style> 