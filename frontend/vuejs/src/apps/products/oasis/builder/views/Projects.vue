<template>
  <BuilderLayout storage-key="projectsViewSidebarCollapsed">
    <!-- Custom Sidebar Content with docs-style design -->
    <template #sidebar-content="{ collapsed }">
      <div class="p-4">
        <div class="mb-6">
          <div class="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3" v-if="!collapsed">
            Navigation
          </div>
          <ul class="space-y-1">
            <li v-for="item in navigationItems" :key="item.name">
              <router-link
                :to="item.to"
                class="group block px-3 py-2 rounded-xl transition-all duration-200 cursor-pointer"
                :class="[
                  isActiveRoute(item.to, item.exact) 
                    ? 'bg-gradient-to-r from-indigo-500/20 to-violet-500/20 text-indigo-300 border border-indigo-400/20' 
                    : 'hover:bg-white/5 text-gray-300 hover:text-white border border-transparent hover:border-white/10'
                ]"
              >
                <div class="flex items-center">
                  <i :class="[item.icon, collapsed ? '' : 'mr-3', 'w-4 text-center text-sm']"></i>
                  <span v-if="!collapsed" class="text-sm font-medium">{{ item.name }}</span>
                </div>
              </router-link>
            </li>
          </ul>
        </div>
      </div>
    </template>

    <!-- Enhanced Main Content with Dynamic Background -->
    <div class="min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Improved Decorative Background Elements -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px] animate-float-delay"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Enhanced Content Container -->
      <div class="relative z-10">
        <!-- Modern Welcome Header Section -->
        <div class="pt-16 pb-12 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-8">
              <div class="space-y-6 md:max-w-3xl">
                <!-- Enhanced Badge -->
                <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full">
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">PROJECT COLLECTION</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h2 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Manage & Organize</span> 
                  <br class="hidden sm:block" />Your Applications
                </h2>
                
                <!-- Enhanced Description -->
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
            <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent my-12 animate-pulse-slow"></div>
          </div>
        </div>

        <!-- Enhanced Project Section with Modern Layout -->
        <div class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-7xl mx-auto">
            <!-- Unified Project Library Container with modern styling -->
            <div class="relative rounded-2xl border border-dark-800/60 bg-dark-900/80 backdrop-blur-lg shadow-lg shadow-dark-900/20 overflow-hidden">
              <!-- Purple gradient header line at the top of the project library -->
              <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-violet-500"></div>
              
              <div class="p-8">
                <!-- Subtle background gradient -->
                <div class="absolute inset-0 bg-gradient-to-br opacity-5 -z-10 from-indigo-900 to-violet-900"></div>
                
                <!-- Subtle glowing orb effect -->
                <div class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-5 blur-3xl bg-indigo-500"></div>
                
                <!-- Header Section -->
                <div class="relative z-10 mb-8">
                  <!-- Badge -->
                  <div class="inline-flex items-center px-4 py-1.5 bg-indigo-500/10 rounded-full mb-4">
                    <span class="text-indigo-400 font-semibold text-sm tracking-wider">YOUR PROJECTS</span>
                  </div>
                  
                  <!-- Header with title and project count -->
                  <div class="relative mb-6">
                    <!-- Project count positioned in top-right corner -->
                    <div class="absolute top-0 right-0 group">
                      <!-- Glow effect on hover -->
                      <div class="absolute -inset-1 rounded-xl bg-gradient-to-r from-indigo-500/30 to-violet-500/30 opacity-0 group-hover:opacity-100 blur-sm transition-all duration-300"></div>
                      
                      <!-- Icon container with updated styling -->
                      <div class="relative bg-dark-800/60 backdrop-blur-sm rounded-xl border border-dark-800/60 hover:border-indigo-500/30 transition-all duration-300 p-3 flex items-center gap-3 shadow-lg shadow-dark-900/20">
                        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500/15 to-violet-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-indigo-500/20 shadow-md shadow-indigo-500/5">
                          <i class="fas fa-folder-open text-indigo-300 text-sm"></i>
                        </div>
                        <div>
                          <p class="text-xs text-gray-400 uppercase">Total</p>
                          <p class="text-xl font-bold text-white">{{ projects.length || 0 }}</p>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Centered title and description -->
                    <div class="flex flex-col items-center justify-center pt-2 pb-2">
                      <div class="space-y-4 text-center w-full">
                        <h2 class="text-2xl font-bold text-white mb-2">Project Library</h2>
                        <p class="text-gray-300">Continue working on your existing web applications</p>
                        <!-- Decorative element - centered on all screen sizes -->
                        <div class="w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto"></div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Search Input - Centered below title -->
                  <div v-if="projects.length > 0" class="mb-6 flex justify-center">
                    <div class="w-full max-w-md">
                      <ProjectSearchInput 
                        v-model="searchQuery"
                        placeholder="Search projects"
                      />
                    </div>
                  </div>
                </div>

                <!-- Content Section -->
                <div class="relative z-10">
                  <!-- Loading State -->
                  <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
                    <div class="w-16 h-16 bg-gradient-to-br from-indigo-500/15 to-violet-500/15 rounded-full flex items-center justify-center mb-5 animate-pulse border border-indigo-500/20 shadow-lg shadow-indigo-500/10">
                      <i class="fas fa-spinner fa-spin text-2xl text-indigo-400"></i>
                    </div>
                    <p class="text-gray-300 text-lg">Loading your projects...</p>
                  </div>

                  <!-- Error State -->
                  <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
                    <div class="w-16 h-16 bg-gradient-to-r from-red-500/15 to-orange-500/15 rounded-full flex items-center justify-center mb-5 border border-red-500/20 shadow-lg shadow-red-500/10">
                      <i class="fas fa-exclamation-circle text-2xl text-red-400"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-white mb-2">Connection Error</h3>
                    <p class="text-gray-300 mb-6 text-center max-w-md">{{ error }}</p>
                    <button
                      @click="retryFetch"
                      class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 border border-indigo-500/40 hover:border-indigo-400/50 text-white rounded-xl shadow-lg hover:shadow-indigo-500/20 transform hover:-translate-y-1 transition-all duration-300 inline-flex items-center"
                    >
                      <i class="fas fa-sync-alt mr-2"></i>
                      Try Again
                    </button>
                  </div>

                  <!-- Empty State -->
                  <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center py-16">
                    <div class="w-16 h-16 bg-gradient-to-br from-indigo-500/15 to-violet-500/15 rounded-full flex items-center justify-center mb-5 border border-indigo-500/20 shadow-lg shadow-indigo-500/10">
                      <i class="fas fa-folder-open text-2xl text-indigo-400"></i>
                    </div>
                    <h3 class="text-xl font-semibold text-white mb-2">No projects yet</h3>
                    <p class="text-gray-300 text-center max-w-md mb-6">Create your first project to start building with Imagi</p>
                    
                    <!-- Directional hint -->
                    <div class="flex items-center text-indigo-400 animate-pulse-slow mb-8">
                      <i class="fas fa-long-arrow-alt-up text-lg mr-2"></i>
                      <span>Get started with a new project</span>
                    </div>
                    
                    <button
                      @click="$router.push({ name: 'builder-dashboard' })"
                      class="px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:-translate-y-1 transition-all duration-300 inline-flex items-center"
                    >
                      <i class="fas fa-plus mr-2"></i>
                      Create Your First Project
                    </button>
                  </div>

                  <!-- Projects Grid -->
                  <div v-else>
                    <!-- If searching, show message -->
                    <div v-if="searchQuery && filteredProjects.length === 0" class="flex flex-col items-center justify-center py-16">
                      <div class="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mb-5">
                        <i class="fas fa-search text-2xl text-indigo-400"></i>
                      </div>
                      <h3 class="text-xl font-semibold text-white mb-2">No matching projects</h3>
                      <p class="text-gray-300 text-center max-w-md">No projects found matching "{{ searchQuery }}"</p>
                    </div>
                    
                    <!-- All Projects Grid -->
                    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      <ProjectCardWithDescription
                        v-for="project in displayedProjects"
                        :key="project.id"
                        :project="project"
                        :editing-description="editingDescription"
                        :edited-description="editedDescription"
                        @start-edit="startEditDescription"
                        @save-description="saveDescription"
                        @cancel-edit="cancelEditDescription"
                        @delete="confirmDelete"
                        @open="openProject"
                        @update:edited-description="editedDescription = $event"
                      />
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
import { computed, onMounted, onActivated, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts';
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore';
import { useNotification } from '@/shared/composables/useNotification';
import { useConfirm } from '../composables/useConfirm';
import ProjectSearchInput from '../components/atoms/ProjectSearchInput.vue';
import ProjectCardWithDescription from '../components/molecules/cards/ProjectCardWithDescription.vue';

const router = useRouter();
const route = useRoute();
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

// Use the project search composable
import { useProjectSearch } from '../composables/useProjectSearch';
const { searchQuery, filteredProjects } = useProjectSearch(sortedProjects);

// Computed property for displayed projects
const displayedProjects = computed(() => {
  return filteredProjects.value;
});

// Projects are displayed through displayedProjects computed property from useProjectSearch

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

// Check if a route is active (exact match or starts with path for nested routes)
const isActiveRoute = (path, exact) => {
  if (exact) {
    return route.path === path
  }
  return route.path.startsWith(path)
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
    // First clear the cache to ensure fresh data
    projectStore.clearProjectsCache();
    
    await projectStore.deleteProject(project.id);
    
    // Immediately refresh the projects list to show updated state
    try {
      await fetchProjects(true); // Force refresh to get latest state from API
    } catch (refreshError) {
      console.warn('Failed to refresh projects after deletion:', refreshError);
    }
    
    showNotification({
      type: 'error',
      message: `Project "${project.name}" deleted`,
      duration: 4000
    });
  } catch (err) {
    console.error('Error deleting project:', err);
    
    // Check if the error is actually a success (project was deleted but API returned unexpected response)
    if (err.response?.status === 404) {
      // Project is gone, which means deletion was successful
      // Clear cache and refresh
      projectStore.clearProjectsCache();
      
      showNotification({
        type: 'error',
        message: `Project "${project.name}" deleted`,
        duration: 4000
      });
      
      // Still refresh the projects list
      try {
        await fetchProjects(true);
      } catch (refreshError) {
        console.warn('Failed to refresh projects after deletion:', refreshError);
      }
    } else {
      // Actual error occurred
      showNotification({
        type: 'error',
        message: err?.message || `Failed to delete project "${project.name}"`,
        duration: 5000
      });
    }
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
    await projectStore.updateProject(project.id, {
      description: editedDescription.value.trim()
    });
    
    // Immediately refresh the projects list to show updated state
    try {
      await fetchProjects(true); // Force refresh to get latest state from API
    } catch (refreshError) {
      console.warn('Failed to refresh projects after description update:', refreshError);
    }
    
    showNotification({
      type: 'success',
      message: 'Project description updated'
    });
    
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

async function fetchProjects(force = true) {
  try {
    // Always force refresh to get the latest state from API
    await projectStore.fetchProjects(force);
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

  const projectId = String(project.id);
  
  router.push({
    name: 'builder-workspace',
    params: { projectId }
  });
}

onMounted(async () => {
  try {
    // Always force refresh to get the latest projects from API
    await fetchProjects(true);
  } catch (err) {
    console.error('Failed to fetch projects on mount:', err);
    showNotification({
      type: 'error',
      message: 'Failed to load projects. Please try again.'
    });
  }
});

// Add support for keep-alive to refresh when component is re-activated
onActivated(async () => {
  console.debug('Projects page activated - refreshing projects from API');
  try {
    // Always force refresh projects when the component is activated
    await fetchProjects(true); // Force refresh to get latest state from API
  } catch (error) {
    console.error('Failed to refresh projects on activation:', error);
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
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: theme('colors.gray.700');
  border-radius: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: theme('colors.gray.600');
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

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
</style>
