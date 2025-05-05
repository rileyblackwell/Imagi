<template>
  <BuilderLayout 
    storage-key="projectsViewSidebarCollapsed"
    :navigation-items="navigationItems"
  >
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects with animated elements -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Improved gradient orbs with subtle animations -->
        <div class="absolute top-[5%] left-[5%] w-[400px] sm:w-[600px] md:w-[900px] h-[400px] sm:h-[600px] md:h-[900px] rounded-full bg-indigo-600/5 blur-[100px] sm:blur-[150px] animate-float"></div>
        <div class="absolute bottom-[10%] right-[5%] w-[300px] sm:w-[500px] md:w-[700px] h-[300px] sm:h-[500px] md:h-[700px] rounded-full bg-violet-500/5 blur-[80px] sm:blur-[120px] animate-float-delay"></div>
        
        <!-- Subtle grid pattern and noise -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.02]"></div>
        
        <!-- Animated accent lines -->
        <div class="absolute left-0 right-0 top-1/4 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10">
        <!-- Modern Header with enhanced layout -->
        <div class="pt-16 pb-10 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-8">
              <div class="space-y-6 md:max-w-3xl">
                <!-- Enhanced badge with animated dot -->
                <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full">
                  <div class="w-2 h-2 rounded-full bg-indigo-400 mr-2 animate-pulse"></div>
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">PROJECT COLLECTION</span>
                </div>
                
                <!-- Modern title with gradient text -->
                <h2 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Manage & Organize</span> 
                  <br class="hidden sm:block" />Your Applications
                </h2>
                
                <!-- Enhanced description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  Access all your web applications in one place. Edit descriptions, track updates, and continue building.
                </p>
              </div>
              
              <!-- Enhanced CTA button -->
              <div>
                <button
                  @click="$router.push({ name: 'builder-dashboard' })"
                  class="group relative overflow-hidden inline-flex items-center px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:-translate-y-1 transition-all duration-300"
                >
                  <!-- Animated glow effect -->
                  <span class="absolute inset-0 bg-white/20 blur-md opacity-0 group-hover:opacity-20 transition-opacity duration-300"></span>
                  <span class="relative flex items-center">
                    <i class="fas fa-plus mr-2.5"></i>
                    Create New Project
                  </span>
                </button>
              </div>
            </div>
            
            <!-- Animated Divider Line -->
            <div class="w-full h-px bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent my-10 animate-pulse-slow"></div>
          </div>
        </div>

        <!-- Project Grid with Enhanced Layout and Filters -->
        <div class="px-6 sm:px-8 lg:px-12 pb-20">
          <div class="max-w-7xl mx-auto">
            <!-- Project Tools and Search Bar -->
            <div v-if="projects.length > 0" class="mb-8">
              <div class="bg-dark-900/60 backdrop-blur-sm rounded-xl border border-gray-800/60 p-4 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
                <!-- Project stats -->
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-indigo-500/15 flex items-center justify-center">
                    <i class="fas fa-folder text-indigo-400"></i>
                  </div>
                  <div>
                    <p class="text-gray-400 text-sm">Total Projects</p>
                    <p class="text-white font-bold text-xl">{{ projects.length }}</p>
                  </div>
                </div>
                
                <!-- Modern search input -->
                <div class="relative group flex-1 max-w-md">
                  <div class="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-lg blur-[2px] opacity-0 group-focus-within:opacity-100 transition-all duration-300 pointer-events-none"></div>
                  <div class="relative flex items-center">
                    <i class="fas fa-search text-gray-500 absolute left-4"></i>
                    <input
                      v-model="searchQuery"
                      type="text"
                      placeholder="Search projects by name or description..."
                      class="relative z-10 w-full pl-10 pr-4 py-3 bg-dark-900/90 border border-dark-600 focus:border-transparent rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200"
                    >
                  </div>
                </div>
              </div>
            </div>

            <!-- Loading State with Enhanced Animation -->
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
              <div class="relative w-20 h-20">
                <div class="absolute inset-0 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 opacity-20 blur-md animate-pulse"></div>
                <div class="relative w-full h-full flex items-center justify-center">
                  <i class="fas fa-spinner fa-spin text-3xl text-indigo-400"></i>
                </div>
              </div>
              <p class="text-gray-300 text-lg mt-6">Loading your projects...</p>
            </div>

            <!-- Error State with Enhanced Design -->
            <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
              <div class="relative w-20 h-20 mb-6">
                <div class="absolute inset-0 rounded-full bg-red-500/20 blur-md"></div>
                <div class="relative w-full h-full flex items-center justify-center">
                  <i class="fas fa-exclamation-circle text-3xl text-red-400"></i>
                </div>
              </div>
              <h3 class="text-xl font-semibold text-white mb-2">Connection Error</h3>
              <p class="text-gray-300 mb-8 text-center max-w-md">{{ error }}</p>
              <button
                @click="retryFetch"
                class="group relative overflow-hidden px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:-translate-y-1 transition-all duration-300"
              >
                <span class="absolute inset-0 bg-white/20 blur-md opacity-0 group-hover:opacity-20 transition-opacity duration-300"></span>
                <span class="relative flex items-center">
                  <i class="fas fa-sync-alt mr-2.5"></i>
                  Try Again
                </span>
              </button>
            </div>

            <!-- Empty State with Enhanced Design -->
            <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center py-16">
              <div class="relative w-20 h-20 mb-6">
                <div class="absolute inset-0 rounded-full bg-indigo-500/20 blur-md"></div>
                <div class="relative w-full h-full flex items-center justify-center">
                  <i class="fas fa-folder-open text-3xl text-indigo-400"></i>
                </div>
              </div>
              <h3 class="text-xl font-semibold text-white mb-2">No projects yet</h3>
              <p class="text-gray-300 text-center max-w-md mb-8">Create your first project to start building with Imagi</p>
              <button
                @click="$router.push({ name: 'builder-dashboard' })"
                class="group relative overflow-hidden px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:-translate-y-1 transition-all duration-300"
              >
                <span class="absolute inset-0 bg-white/20 blur-md opacity-0 group-hover:opacity-20 transition-opacity duration-300"></span>
                <span class="relative flex items-center">
                  <i class="fas fa-plus mr-2.5"></i>
                  Create Your First Project
                </span>
              </button>
            </div>

            <!-- Enhanced Project Grid with Search Filtering -->
            <div v-else>
              <!-- If searching, show message -->
              <div v-if="searchQuery && filteredProjects.length === 0" class="flex flex-col items-center justify-center py-16 bg-dark-900/40 backdrop-blur-sm border border-gray-800/60 rounded-xl">
                <div class="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mb-5">
                  <i class="fas fa-search text-2xl text-indigo-400"></i>
                </div>
                <h3 class="text-xl font-semibold text-white mb-2">No matching projects</h3>
                <p class="text-gray-300 text-center max-w-md">No projects match your search for "{{ searchQuery }}"</p>
              </div>
              
              <!-- Project Grid with Modern Cards -->
              <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                <div
                  v-for="project in displayedProjects"
                  :key="project.id"
                  class="group relative transform transition-all duration-300 hover:-translate-y-2"
                >
                  <!-- Enhanced glass morphism effect with glow -->
                  <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                  
                  <!-- Card content with enhanced styling -->
                  <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-indigo-500/30 transition-all duration-300">
                    <!-- Card header with gradient -->
                    <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-violet-500"></div>
                    
                    <div class="p-6">
                      <div class="flex items-center gap-4 mb-4">
                        <!-- Enhanced icon with glowing effect -->
                        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-indigo-500/20 shadow-lg shadow-indigo-500/5">
                          <i class="fas fa-cube text-indigo-400 text-lg"></i>
                        </div>
                        <h3 class="text-xl font-semibold text-white truncate group-hover:text-indigo-400 transition-colors">
                          {{ project.name }}
                        </h3>
                      </div>
                      
                      <!-- Description with edit capability -->
                      <div class="mb-6">
                        <div v-if="editingDescription === project.id" class="relative group/input w-full mb-2">
                          <textarea
                            v-model="editedDescription"
                            placeholder="Project description..."
                            class="w-full px-3 py-2 bg-dark-800/60 border border-indigo-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all duration-200 min-h-[80px] resize-y"
                            rows="3"
                            @keydown.esc="cancelEditDescription()"
                          ></textarea>
                          <div class="flex items-center gap-2 mt-2">
                            <button 
                              @click="saveDescription(project)"
                              class="px-3 py-1.5 text-sm bg-indigo-500/20 hover:bg-indigo-500 text-indigo-400 hover:text-white rounded-lg transition-all duration-200 flex items-center"
                            >
                              <i class="fas fa-check mr-1.5"></i> Save
                            </button>
                            <button 
                              @click="cancelEditDescription()"
                              class="px-3 py-1.5 text-sm bg-dark-700/50 hover:bg-dark-600 text-gray-400 hover:text-white rounded-lg transition-all duration-200 flex items-center"
                            >
                              <i class="fas fa-times mr-1.5"></i> Cancel
                            </button>
                          </div>
                        </div>
                        <div v-else class="flex items-center justify-between">
                          <p class="text-gray-400 line-clamp-2 text-sm">
                            {{ project.description || 'No description provided' }}
                          </p>
                          <button 
                            @click="startEditDescription(project)"
                            class="ml-2 text-indigo-400 hover:text-indigo-300 transition-colors"
                            title="Edit description"
                          >
                            <i class="fas fa-edit"></i>
                          </button>
                        </div>
                      </div>
                      
                      <div class="mt-auto">
                        <div class="flex items-center text-sm text-gray-500 mb-4">
                          <i class="fas fa-clock text-xs opacity-70 mr-2"></i>
                          Last updated {{ formatDate(project.updated_at) }}
                        </div>
                        
                        <div class="flex items-center gap-3">
                          <!-- Open project button with enhanced hover effect -->
                          <button
                            @click="openProject(project)"
                            class="flex-1 py-3 px-4 text-indigo-400 hover:text-white transition-all duration-200 rounded-lg bg-indigo-500/10 hover:bg-gradient-to-r hover:from-indigo-500 hover:to-violet-500 transform hover:scale-105 shadow-md shadow-indigo-500/5 hover:shadow-lg hover:shadow-indigo-500/20"
                            title="Open project"
                          >
                            <i class="fas fa-arrow-right mr-2"></i>
                            Open Project
                          </button>
                          
                          <!-- Delete button with enhanced hover effect -->
                          <button
                            @click="confirmDelete(project)"
                            class="p-3 text-red-400 hover:text-white transition-all duration-200 rounded-lg bg-red-500/10 hover:bg-red-500 transform hover:scale-105 shadow-md shadow-red-500/5 hover:shadow-lg hover:shadow-red-500/20"
                            title="Delete project"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BuilderLayout>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts';
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore';
import { useNotification } from '@/shared/composables/useNotification';
import { useConfirm } from '../composables/useConfirm';

const router = useRouter();
const projectStore = useProjectStore();
const { showNotification } = useNotification();
const { confirm } = useConfirm();

const projects = computed(() => projectStore.projects);
const sortedProjects = computed(() => projectStore.sortedProjects);
const isLoading = computed(() => projectStore.loading);
const error = computed(() => projectStore.error);

// Description editing state
const editingDescription = ref(null);
const editedDescription = ref('');

// Search functionality
const searchQuery = ref('');
const filteredProjects = computed(() => {
  if (!searchQuery.value.trim()) return sortedProjects.value;
  
  const query = searchQuery.value.toLowerCase().trim();
  return sortedProjects.value.filter(project => 
    project.name.toLowerCase().includes(query) || 
    (project.description && project.description.toLowerCase().includes(query))
  );
});

// Computed property for displayed projects
const displayedProjects = computed(() => {
  return filteredProjects.value;
});

const navigationItems = [
  { 
    name: 'Dashboard',
    to: '/dashboard',
    icon: 'fas fa-home',
    exact: true
  },
  {
    name: 'Oasis Projects',
    to: '/products/oasis/builder/projects',
    icon: 'fas fa-folder',
    exact: true
  },
  {
    name: 'Create Project',
    to: '/products/oasis/builder/dashboard',
    icon: 'fas fa-plus-circle',
    exact: true
  },
  {
    name: 'Buy AI Credits',
    to: '/payments/checkout',
    icon: 'fas fa-money-bill-wave',
    exact: true
  }
];

function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}

async function confirmDelete(project) {
  // Use confirm dialog
  const confirmed = await confirm({
    title: 'Delete Project',
    message: `Are you sure you want to delete "${project.name}"? This action cannot be undone.`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  });
  
  if (!confirmed) return;

  try {
    await projectStore.deleteProject(project.id);
    showNotification({
      type: 'success',
      message: `Project "${project.name}" deleted successfully`,
      duration: 4000 // Shorter duration for better UX
    });
  } catch (err) {
    showNotification({
      type: 'error',
      message: err.response?.data?.error || `Failed to delete project "${project.name}"`,
      duration: 5000
    });
  }
}

function startEditDescription(project) {
  editingDescription.value = project.id;
  editedDescription.value = project.description || '';
}

function cancelEditDescription() {
  editingDescription.value = null;
  editedDescription.value = '';
}

async function saveDescription(project) {
  try {
    // Call API to update the project description
    await projectStore.updateProject(project.id, {
      description: editedDescription.value.trim()
    });
    
    showNotification({
      type: 'success',
      message: 'Project description updated'
    });
    
    // Reset edit state
    cancelEditDescription();
  } catch (err) {
    showNotification({
      type: 'error',
      message: err.response?.data?.error || 'Failed to update project description'
    });
  }
}

async function retryFetch() {
  projectStore.clearError();
  await fetchProjects();
}

async function fetchProjects() {
  try {
    await projectStore.fetchProjects();
  } catch (err) {
    showNotification({
      type: 'error',
      message: 'Failed to fetch projects'
    });
  }
}

function openProject(project) {
  if (!project.id) {
    showNotification({
      type: 'error',
      message: 'Invalid project ID'
    });
    return;
  }

  // Convert ID to string to ensure consistent typing
  const projectId = String(project.id);
  
  // Navigate to the workspace with the project ID
  router.push({
    name: 'builder-workspace',
    params: { projectId }
  });
}

onMounted(async () => {
  // Initialize projects on mount
  try {
    await fetchProjects();
  } catch (err) {
    console.error('Failed to fetch projects on mount:', err);
    showNotification({
      type: 'error',
      message: 'Failed to load projects. Please try again.'
    });
  }
});
</script>

<style scoped>
/* Enhanced scrollbar styling */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.700') transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: theme('colors.gray.700');
  border-radius: 9999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: theme('colors.gray.600');
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient-shift 4s ease infinite;
}

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
}

.delay-700 {
  animation-delay: 700ms;
}

/* Line clamp for description */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
</style>
