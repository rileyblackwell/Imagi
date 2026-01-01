<template>
  <div class="group relative transform transition-all duration-300">
    <!-- Premium glass card matching dashboard style -->
    <div class="relative">
      <!-- Background glow -->
      <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/90 backdrop-blur-xl overflow-hidden h-full flex flex-col transition-all duration-300 hover:border-white/[0.12] hover:-translate-y-1">
        <!-- Accent line -->
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
        
        <!-- Decorative elements -->
        <div class="absolute -bottom-16 -right-16 w-32 h-32 bg-violet-500/5 rounded-full blur-2xl pointer-events-none group-hover:opacity-80 transition-opacity duration-500"></div>
        
        <!-- Content -->
        <div class="relative z-10 p-6 flex flex-col h-full">
          <!-- Project header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <!-- Icon with gradient -->
              <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform duration-300">
                <svg class="w-5 h-5 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
              </div>
              
              <!-- Project name -->
              <div class="flex-1 min-w-0">
                <h3 class="text-base font-semibold text-white/90 truncate leading-tight">{{ project.name }}</h3>
                <div class="flex items-center text-xs text-white/40 mt-1">
                  <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ formatDate(project.updated_at) }}
                </div>
              </div>
            </div>
            
            <!-- Delete button -->
            <button
              @click="$emit('delete', project)"
              class="p-2 text-white/40 hover:text-red-400 transition-all duration-200 rounded-lg hover:bg-red-500/10 border border-white/[0.08] hover:border-red-400/30 flex items-center justify-center w-8 h-8 flex-shrink-0"
              title="Delete project"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
          
          <!-- Separator -->
          <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-4"></div>
          
          <!-- Description with edit capability -->
          <div class="mb-4 flex-grow">
            <div v-if="editingDescription === project.id" class="space-y-3">
              <!-- Editing interface -->
              <div class="relative">
                <label class="block text-xs font-medium text-white/40 mb-2 uppercase tracking-wider">Edit Description</label>
                <textarea
                  :value="editedDescription"
                  @input="$emit('update:editedDescription', $event.target.value)"
                  placeholder="Project description..."
                  class="w-full px-4 py-3 bg-white/[0.03] border border-white/[0.08] focus:border-violet-400/50 hover:border-white/[0.12] rounded-xl text-white/90 placeholder-white/30 transition-all duration-300 resize-none backdrop-blur-sm focus:bg-white/[0.05] text-sm"
                  style="outline: none !important;"
                  rows="3"
                  @keydown.esc="$emit('cancel-edit')"
                ></textarea>
              </div>
              
              <!-- Action buttons -->
              <div class="flex items-center gap-2">
                <button 
                  @click="$emit('save-description', project)"
                  class="px-4 py-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-500 hover:to-fuchsia-500 text-white font-medium rounded-xl shadow-lg shadow-violet-500/25 transition-all duration-200 text-xs flex items-center"
                >
                  <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  Save
                </button>
                <button 
                  @click="$emit('cancel-edit')"
                  class="px-4 py-2 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] hover:border-white/[0.12] text-white/60 hover:text-white/90 rounded-xl transition-all duration-200 text-xs flex items-center"
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
                <p class="text-white/50 text-sm flex-grow line-clamp-3 leading-relaxed">
                  {{ project.description || 'No description provided' }}
                </p>
                <button 
                  @click="$emit('start-edit', project)"
                  class="p-1.5 text-white/40 hover:text-violet-400 transition-all duration-200 rounded-lg hover:bg-white/[0.05] border border-white/[0.08] hover:border-violet-400/30 flex items-center justify-center flex-shrink-0"
                  title="Edit description"
                >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Footer section -->
          <div class="mt-auto">
            <!-- Open button -->
            <button
              @click="$emit('open', project)"
              class="w-full inline-flex items-center justify-center px-4 py-3 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] hover:border-violet-400/30 text-white/90 rounded-xl transition-all duration-300 text-sm font-medium group/button"
              title="Open project workspace"
            >
              <svg class="w-4 h-4 mr-2 group-hover/button:text-violet-400 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
              </svg>
              Open Project
              <i class="fas fa-arrow-right text-xs ml-2 transform group-hover/button:translate-x-1 transition-transform duration-200"></i>
            </button>
          </div>
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

const emit = defineEmits(['start-edit', 'save-description', 'cancel-edit', 'delete', 'open', 'update:editedDescription']);

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