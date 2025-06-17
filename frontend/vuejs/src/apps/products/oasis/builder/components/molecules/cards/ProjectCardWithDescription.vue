<template>
  <div class="group relative transform transition-all duration-300">
    <!-- Modern glassmorphism container matching dashboard style -->
    <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full flex flex-col transition-all duration-300 hover:border-white/20 hover:shadow-black/40 transform hover:-translate-y-1">
      <!-- Sleek gradient header -->
      <div class="h-1 w-full bg-gradient-to-r from-violet-400 via-indigo-400 to-violet-400 opacity-80"></div>
      
      <!-- Subtle background effects -->
      <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-violet-400/4 to-indigo-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
      
      <!-- Content with reduced padding for slender look -->
      <div class="relative z-10 p-5 flex flex-col h-full">
        <!-- Modern project header -->
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <!-- Modern icon with subtle gradient -->
            <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-400/20 to-indigo-400/20 flex items-center justify-center border border-violet-400/20 flex-shrink-0">
              <svg class="w-4 h-4 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
              </svg>
            </div>
            
            <!-- Project name with improved typography -->
            <div class="flex-1 min-w-0">
              <h3 class="text-base font-semibold text-white truncate leading-tight">{{ project.name }}</h3>
              <div class="flex items-center text-xs text-gray-400 mt-1">
                <svg class="w-3 h-3 mr-1.5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                {{ formatDate(project.updated_at) }}
              </div>
            </div>
          </div>
          
          <!-- Sleek Delete button -->
          <button
            @click="$emit('delete', project)"
            class="p-2 text-gray-400 hover:text-red-400 transition-all duration-200 rounded-lg hover:bg-white/5 border border-white/10 hover:border-red-400/30 flex items-center justify-center w-8 h-8 flex-shrink-0"
            title="Delete project"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
          </button>
        </div>
        
        <!-- Modern separator -->
        <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4"></div>
        
        <!-- Description with edit capability -->
        <div class="mb-4 flex-grow">
          <div v-if="editingDescription === project.id" class="space-y-3">
            <!-- Modern editing interface -->
            <div class="relative group/input">
              <div class="absolute inset-0 bg-gradient-to-r from-violet-500/12 to-indigo-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              
              <label class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Edit Description</label>
              <textarea
                :value="editedDescription"
                @input="$emit('update:editedDescription', $event.target.value)"
                placeholder="Project description..."
                class="relative z-10 w-full px-4 py-2.5 bg-white/5 border border-white/10 focus:border-violet-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 resize-none backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-violet-500/20 text-sm"
                style="outline: none !important; box-shadow: none !important;"
                rows="3"
                @keydown.esc="$emit('cancel-edit')"
              ></textarea>
            </div>
            
            <!-- Modern action buttons -->
            <div class="flex items-center gap-2">
              <button 
                @click="$emit('save-description', project)"
                class="px-3 py-2 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-200 text-xs flex items-center"
              >
                <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Save
              </button>
              <button 
                @click="$emit('cancel-edit')"
                class="px-3 py-2 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-white/20 text-gray-400 hover:text-gray-300 rounded-xl transition-all duration-200 text-xs flex items-center"
              >
                <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
                Cancel
              </button>
            </div>
          </div>
          
          <div v-else class="w-full">
            <!-- Project description with edit capability -->
            <div class="flex justify-between items-start gap-3">
              <p class="text-gray-300 text-sm flex-grow line-clamp-3 leading-relaxed">
                {{ project.description || 'No description provided' }}
              </p>
              <button 
                @click="$emit('start-edit', project)"
                class="p-1.5 text-gray-400 hover:text-violet-400 transition-all duration-200 rounded-lg hover:bg-white/5 border border-white/10 hover:border-violet-400/30 flex items-center justify-center flex-shrink-0"
                title="Edit description"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Footer section with modern styling -->
        <div class="mt-auto">
          <!-- Sleek Open button -->
          <button
            @click="$emit('open', project)"
            class="w-full inline-flex items-center justify-center px-4 py-2.5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-violet-400/30 text-white rounded-xl transition-all duration-300 text-sm font-medium group/button"
            title="Open project workspace"
          >
            <svg class="w-4 h-4 mr-2 group-hover/button:text-violet-400 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
            Open Project
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