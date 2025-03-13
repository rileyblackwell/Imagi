<template>
  <BuilderLayout 
    storage-key="projectsViewSidebarCollapsed"
    :navigation-items="navigationItems"
  >
    <div class="min-h-screen bg-dark-900 relative overflow-hidden">
      <!-- Enhanced Background Effects -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Refined gradient background -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-transparent to-violet-500/10"></div>
        
        <!-- Ambient glow effects -->
        <div class="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[800px] bg-gradient-to-r from-primary-500/15 to-violet-500/15 rounded-full blur-[120px] opacity-40"></div>
        <div class="absolute bottom-0 right-0 w-[600px] h-[600px] bg-gradient-to-r from-indigo-500/10 to-primary-500/10 rounded-full blur-[100px] opacity-30"></div>
        
        <!-- Subtle grid pattern -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02] mix-blend-overlay"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10">
        <!-- Enhanced Header -->
        <div class="pt-16 pb-12 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="md:flex md:items-center md:justify-between">
              <div class="flex-1 min-w-0">
                <!-- Imagi Title with Auth Page Styling -->
                <div class="inline-flex items-center justify-center mb-6">
                  <div class="rounded-2xl bg-gradient-to-br p-[1px] from-primary-300/40 to-violet-300/40
                            hover:from-primary-200/50 hover:to-violet-200/50 transition-all duration-300">
                    <div class="px-8 py-4 rounded-2xl bg-dark-800/95 backdrop-blur-xl
                              shadow-[0_0_20px_-5px_rgba(99,102,241,0.4)]">
                      <h1 class="text-4xl font-bold bg-gradient-to-r from-pink-300 via-emerald-300 to-yellow-200 
                                bg-clip-text text-transparent tracking-tight
                                drop-shadow-[0_0_12px_rgba(236,72,153,0.3)]
                                animate-gradient">
                        Imagi
                      </h1>
                    </div>
                  </div>
                </div>
                
                <h2 class="text-3xl font-bold text-white tracking-tight">All Projects</h2>
                <p class="mt-3 text-lg text-gray-300/90 max-w-2xl leading-relaxed">
                  Manage and organize all your web applications in one place
                </p>
              </div>
              <div class="mt-6 md:mt-0 md:ml-4">
                <button
                  @click="$router.push({ name: 'builder-dashboard' })"
                  class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 text-white rounded-xl hover:from-primary-600 hover:to-violet-600 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:translate-y-[-2px] transition-all duration-300"
                >
                  <i class="fas fa-plus mr-2.5"></i>
                  Create New Project
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Project List with Enhanced Styling -->
        <div class="px-6 sm:px-8 lg:px-12 pb-20">
          <div class="max-w-7xl mx-auto">
            <!-- Loading State -->
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
              <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mb-5 animate-pulse">
                <i class="fas fa-spinner fa-spin text-2xl text-primary-400"></i>
              </div>
              <p class="text-gray-400 text-lg">Loading your projects...</p>
            </div>

            <!-- Error State -->
            <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
              <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-5">
                <i class="fas fa-exclamation-circle text-2xl text-red-400"></i>
              </div>
              <p class="text-gray-400 mb-6 text-center max-w-md">{{ error }}</p>
              <button
                @click="retryFetch"
                class="px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:translate-y-[-2px] transition-all duration-300"
              >
                <i class="fas fa-sync-alt mr-2"></i>
                Try Again
              </button>
            </div>

            <!-- Empty State -->
            <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center py-16">
              <div class="w-16 h-16 bg-dark-700 rounded-full flex items-center justify-center mb-5">
                <i class="fas fa-folder-open text-2xl text-gray-400"></i>
              </div>
              <p class="text-gray-400 text-center text-lg mb-6">No projects yet. Create your first project to get started!</p>
              <button
                @click="$router.push({ name: 'builder-dashboard' })"
                class="px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 hover:from-primary-600 hover:to-violet-600 text-white rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:translate-y-[-2px] transition-all duration-300"
              >
                <i class="fas fa-plus mr-2"></i>
                Create Your First Project
              </button>
            </div>

            <!-- Project Grid -->
            <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div
                v-for="project in sortedProjects"
                :key="project.id"
                class="group relative transform transition-all duration-300 hover:translate-y-[-3px]"
              >
                <!-- Enhanced hover glow effect -->
                <div class="absolute -inset-[1px] rounded-xl bg-gradient-to-r from-primary-500/30 via-violet-500/30 to-indigo-500/30 opacity-0 group-hover:opacity-100 blur-[2px] transition-all duration-300"></div>
                
                <!-- Card content with enhanced styling -->
                <div class="relative bg-dark-800/80 backdrop-blur-md rounded-xl p-7 border border-dark-700/80 group-hover:border-primary-500/30 transition-all duration-300 shadow-lg shadow-dark-950/30 group-hover:shadow-xl group-hover:shadow-primary-500/10 h-full flex flex-col">
                  <div class="flex items-center gap-4 mb-4">
                    <!-- Enhanced icon container with animation -->
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20 shadow-md shadow-primary-500/5">
                      <i class="fas fa-cube text-primary-400 text-lg"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-white truncate group-hover:text-primary-400/90 transition-colors">
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
                        class="flex-1 p-3 text-primary-400 hover:text-white transition-all duration-200 rounded-lg bg-primary-500/10 hover:bg-primary-500 hover:scale-105 shadow-md shadow-primary-500/5 hover:shadow-lg hover:shadow-primary-500/20"
                        title="Open project"
                      >
                        <i class="fas fa-arrow-right mr-2"></i>
                        Open Project
                      </button>
                      
                      <!-- Delete button with enhanced hover effect -->
                      <button
                        @click="confirmDelete(project)"
                        class="p-3 text-red-400 hover:text-white transition-all duration-200 rounded-lg bg-red-500/10 hover:bg-red-500 hover:scale-105 shadow-md shadow-red-500/5 hover:shadow-lg hover:shadow-red-500/20"
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
      message: 'Project ID is missing or invalid'
    });
    return;
  }
  
  const projectId = String(project.id);
  
  // Navigate to workspace with proper ID
  router.push({
    name: 'builder-workspace',
    params: { projectId }
  });
}

onMounted(fetchProjects);
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

/* Line clamp for description */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
