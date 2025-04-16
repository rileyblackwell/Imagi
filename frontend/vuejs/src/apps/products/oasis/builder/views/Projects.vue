<template>
  <BuilderLayout 
    storage-key="projectsViewSidebarCollapsed"
    :navigation-items="navigationItems"
  >
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching Home landing page -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Gradient orbs matching Home landing page -->
        <div class="absolute top-[10%] left-[5%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-primary-500/5 blur-[80px] sm:blur-[120px] animate-float"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-violet-500/5 blur-[60px] sm:blur-[100px] animate-float-delay"></div>
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10">
        <!-- Enhanced Header -->
        <div class="pt-20 pb-16 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="md:flex md:items-center md:justify-between">
              <div class="flex-1 min-w-0">
                <!-- Enhanced section header to match home landing page -->
                <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-3">
                  <span class="text-primary-400 font-semibold text-sm tracking-wider">YOUR PROJECTS</span>
                </div>
                
                <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">Project Collection</h2>
                <p class="text-xl text-gray-300 max-w-3xl leading-relaxed">
                  Manage and organize all your web applications in one place
                </p>
              </div>
              <div class="mt-6 md:mt-0 md:ml-4">
                <button
                  @click="$router.push({ name: 'builder-dashboard' })"
                  class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 text-white rounded-xl hover:from-primary-600 hover:to-violet-600 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:-translate-y-1 transition-all duration-300"
                >
                  <i class="fas fa-plus mr-2.5"></i>
                  Create New Project
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Divider with animated line matching Home page -->
        <div class="relative h-16 max-w-7xl mx-auto">
          <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
        </div>

        <!-- Project List with Enhanced Styling -->
        <div class="px-6 sm:px-8 lg:px-12 pb-20">
          <div class="max-w-7xl mx-auto">
            <!-- Loading State -->
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
              <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mb-5 animate-pulse">
                <i class="fas fa-spinner fa-spin text-2xl text-primary-400"></i>
              </div>
              <p class="text-gray-300 text-lg">Loading your projects...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
              <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-5">
                <i class="fas fa-exclamation-circle text-2xl text-red-400"></i>
              </div>
              <p class="text-gray-300 mb-6 text-center max-w-md">{{ error }}</p>
              <button
                @click="retryFetch"
                class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:-translate-y-1 transition-all duration-300"
              >
                <i class="fas fa-sync-alt mr-2"></i>
                Try Again
              </button>
            </div>

            <!-- Empty State -->
            <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center py-16">
              <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mb-5">
                <i class="fas fa-folder-open text-2xl text-primary-400"></i>
              </div>
              <h3 class="text-xl font-semibold text-white mb-2">No projects yet</h3>
              <p class="text-gray-300 text-center max-w-md mb-6">Create your first project to start building with Imagi</p>
              <button
                @click="$router.push({ name: 'builder-dashboard' })"
                class="px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 hover:from-primary-600 hover:to-violet-600 text-white rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:-translate-y-1 transition-all duration-300"
              >
                <i class="fas fa-plus mr-2"></i>
                Create Your First Project
              </button>
            </div>

            <!-- Project Grid -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div
                v-for="project in sortedProjects"
                :key="project.id"
                class="group relative transform transition-all duration-300 hover:-translate-y-2"
              >
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <!-- Card content with enhanced styling -->
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-3 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                  
                  <div class="p-6">
                    <div class="flex items-center gap-4 mb-4">
                      <!-- Enhanced icon with glowing effect -->
                      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/20 to-violet-500/20 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20 shadow-lg shadow-primary-500/5">
                        <i class="fas fa-cube text-primary-400 text-lg"></i>
                      </div>
                      <h3 class="text-xl font-semibold text-white truncate group-hover:text-primary-400 transition-colors">
                        {{ project.name }}
                      </h3>
                    </div>
                    
                    <p class="text-gray-400 mb-6 line-clamp-2 text-sm">
                      {{ project.description || 'No description provided' }}
                    </p>
                    
                    <div class="mt-auto">
                      <div class="flex items-center text-sm text-gray-500 mb-4">
                        <i class="fas fa-clock text-xs opacity-70 mr-2"></i>
                        Last updated {{ formatDate(project.updated_at) }}
                      </div>
                      
                      <div class="flex items-center gap-3">
                        <!-- Open project button with enhanced hover effect -->
                        <button
                          @click="openProject(project)"
                          class="flex-1 py-3 px-4 text-primary-400 hover:text-white transition-all duration-200 rounded-lg bg-primary-500/10 hover:bg-gradient-to-r hover:from-primary-500 hover:to-violet-500 transform hover:scale-105 shadow-md shadow-primary-500/5 hover:shadow-lg hover:shadow-primary-500/20"
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
  </BuilderLayout>
</template>

<script setup>
import { computed, onMounted } from 'vue';
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

const navigationItems = [
  { 
    name: 'Main Dashboard',
    to: '/dashboard',
    icon: 'fas fa-th-large',
    exact: true
  },
  {
    name: 'Projects',
    to: '/products/oasis/builder/projects',
    icon: 'fas fa-folder',
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
      message: 'Project deleted successfully'
    });
  } catch (err) {
    showNotification({
      type: 'error',
      message: err.response?.data?.error || 'Failed to delete project'
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

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
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

/* Line clamp for description */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
