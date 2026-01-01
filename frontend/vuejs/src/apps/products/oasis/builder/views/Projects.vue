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

    <!-- Premium Main Content - Matching Home Page & Dashboard -->
    <div class="min-h-screen bg-[#050508] relative overflow-hidden">
      <!-- Premium Background System -->
      <div class="fixed inset-0 pointer-events-none">
        <!-- Base gradient mesh -->
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_120%_80%_at_50%_-20%,rgba(120,119,198,0.15),transparent_50%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_80%_50%,rgba(78,68,206,0.08),transparent_40%)]"></div>
        <div class="absolute inset-0 bg-[radial-gradient(ellipse_60%_40%_at_10%_80%,rgba(167,139,250,0.06),transparent_35%)]"></div>
        
        <!-- Subtle grain texture -->
        <div class="absolute inset-0 opacity-[0.015]" style="background-image: url('data:image/svg+xml,%3Csvg viewBox=%220 0 256 256%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noise%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.8%22 numOctaves=%224%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/%3E%3C/svg%3E');"></div>
        
        <!-- Animated aurora effect -->
        <div class="absolute top-0 left-1/4 right-1/4 h-[600px] opacity-30">
          <div class="absolute inset-0 bg-gradient-to-b from-violet-500/20 via-fuchsia-500/10 to-transparent blur-[100px] animate-aurora"></div>
        </div>
        
        <!-- Floating orbs -->
        <div class="absolute top-[20%] right-[10%] w-[500px] h-[500px] rounded-full bg-gradient-to-br from-indigo-600/8 to-violet-600/4 blur-[120px] animate-float-slow"></div>
        <div class="absolute bottom-[10%] left-[5%] w-[400px] h-[400px] rounded-full bg-gradient-to-tr from-fuchsia-600/6 to-purple-600/3 blur-[100px] animate-float-delayed"></div>
        <div class="absolute top-[60%] right-[30%] w-[300px] h-[300px] rounded-full bg-gradient-to-bl from-amber-500/4 to-orange-500/2 blur-[80px] animate-float-reverse"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10">
        <!-- Premium Header Section - Matching Home Page & Dashboard -->
        <div class="pt-20 pb-12 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="text-center">
              <!-- Animated badge matching home page -->
              <div class="mb-8 inline-block animate-fade-in">
                <div class="group inline-flex items-center gap-3 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] backdrop-blur-sm hover:bg-white/[0.05] hover:border-white/[0.12] transition-all duration-300 cursor-default">
                  <span class="relative flex h-2 w-2">
                    <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75"></span>
                    <span class="relative inline-flex rounded-full h-2 w-2 bg-violet-400"></span>
                  </span>
                  <span class="text-sm font-medium text-white/70 tracking-wide">Project Collection</span>
                </div>
              </div>
              
              <!-- Title with gradient text -->
              <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight mb-6 leading-[1.1]">
                <span class="block text-white/90">Manage & Organize</span>
                <span class="block mt-2">
                  <span class="relative inline-block">
                    <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                      Your Applications
                    </span>
                    <span class="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-400/50 to-transparent"></span>
                  </span>
                </span>
              </h1>
              
              <!-- Description -->
              <p class="text-lg sm:text-xl text-white/50 mb-10 max-w-2xl mx-auto leading-relaxed">
                Access all your web applications in one place. Edit descriptions, track updates, and continue building.
              </p>
              
              <!-- CTA button -->
              <button
                @click="$router.push({ name: 'builder-dashboard' })"
                class="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
              >
                <i class="fas fa-plus"></i>
                Create New Project
                <i class="fas fa-arrow-right text-sm transform group-hover:translate-x-1 transition-transform duration-300"></i>
              </button>
            </div>
            
            <!-- Elegant Divider -->
            <div class="relative py-8 md:py-12">
              <div class="relative flex items-center justify-center">
                <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
                <div class="mx-6 flex items-center gap-2">
                  <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
                  <div class="w-1.5 h-1.5 rounded-full bg-violet-400/70"></div>
                  <div class="w-1 h-1 rounded-full bg-violet-400/50"></div>
                </div>
                <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Project Section with Premium Glass Card -->
        <div class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-7xl mx-auto">
            <!-- Premium glass card - Matching Dashboard Style -->
            <div class="group relative">
              <!-- Background glow -->
              <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
              
              <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden">
                <!-- Accent line -->
                <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                
                <!-- Decorative elements -->
                <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
                <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
                
                <!-- Content -->
                <div class="relative z-10 p-6 md:p-8">
                  <!-- Header Section -->
                  <div class="mb-8">
                    <!-- Badge matching home page -->
                    <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-4">
                      <i class="fas fa-folder text-xs text-violet-400/80"></i>
                      <span class="text-sm font-medium text-white/60">Your Projects</span>
                    </div>
                    
                    <!-- Title and count -->
                    <div class="flex items-center justify-between mb-6">
                      <div>
                        <h3 class="text-2xl font-semibold text-white/90 leading-tight mb-2">Project Library</h3>
                        <p class="text-white/50 text-sm leading-relaxed">Continue working on your existing applications</p>
                      </div>
                      
                      <!-- Project count badge -->
                      <div class="inline-flex items-center gap-3 px-4 py-3 bg-white/[0.03] rounded-xl border border-white/[0.08]">
                        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 flex items-center justify-center">
                          <i class="fas fa-folder-open text-violet-400"></i>
                        </div>
                        <div>
                          <p class="text-xs text-white/40 uppercase tracking-wider">Total</p>
                          <p class="text-xl font-bold text-white/90">{{ projects.length || 0 }}</p>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Search Input -->
                    <div v-if="projects.length > 0" class="max-w-md">
                      <SearchInput 
                        v-model="searchQuery"
                        placeholder="Search projects"
                        variant="project"
                      />
                    </div>
                  </div>

                  <!-- Content Section -->
                  <div>
                    <!-- Loading State -->
                    <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
                      <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 mb-4">
                        <div class="w-6 h-6 border-2 border-violet-400/30 border-t-violet-400 rounded-full animate-spin"></div>
                      </div>
                      <p class="text-white/50 text-sm">Loading your projects...</p>
                    </div>

                    <!-- Error State -->
                    <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
                      <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-red-500/20 to-orange-500/20 border border-red-500/20 mb-4">
                        <i class="fas fa-exclamation-triangle text-red-400 text-xl"></i>
                      </div>
                      <h3 class="text-lg font-medium text-white/90 mb-1">Connection Error</h3>
                      <p class="text-white/50 mb-6 text-center max-w-md text-sm">{{ error }}</p>
                      <button
                        @click="retryFetch"
                        class="group/btn inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
                      >
                        <i class="fas fa-redo text-sm"></i>
                        <span>Try Again</span>
                      </button>
                    </div>

                    <!-- Empty State -->
                    <div v-else-if="projects.length === 0" class="flex flex-col items-center justify-center py-16">
                      <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 mb-4">
                        <i class="fas fa-folder-open text-violet-400 text-xl"></i>
                      </div>
                      <h3 class="text-lg font-medium text-white/90 mb-1">No projects yet</h3>
                      <p class="text-white/50 text-center max-w-md mb-6 text-sm">Create your first project to start building with Imagi</p>
                      
                      <!-- Directional hint -->
                      <div class="flex items-center text-violet-400 text-sm mb-6">
                        <i class="fas fa-arrow-up mr-2 animate-pulse"></i>
                        <span>Get started with a new project</span>
                      </div>
                      
                      <button
                        @click="$router.push({ name: 'builder-dashboard' })"
                        class="group inline-flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5"
                      >
                        <i class="fas fa-plus"></i>
                        Create Your First Project
                        <i class="fas fa-arrow-right text-sm transform group-hover:translate-x-1 transition-transform duration-300"></i>
                      </button>
                    </div>

                    <!-- Projects Grid -->
                    <div v-else>
                      <!-- If searching, show message -->
                      <div v-if="searchQuery && filteredProjects.length === 0" class="flex flex-col items-center justify-center py-16">
                        <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/[0.08] mb-4">
                          <i class="fas fa-search text-white/40 text-xl"></i>
                        </div>
                        <h3 class="text-lg font-medium text-white/90 mb-1">No matching projects</h3>
                        <p class="text-white/50 text-center max-w-md text-sm">No projects found matching "{{ searchQuery }}"</p>
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
import { SearchInput } from '../components/atoms';
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
/* Fade in animation */
@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-fade-in {
  animation: fade-in 0.8s ease-out forwards;
}

/* Gradient animation */
@keyframes gradient-x {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.animate-gradient-x {
  animation: gradient-x 4s ease infinite;
}

/* Aurora animation */
@keyframes aurora {
  0%, 100% {
    transform: translateX(-10%) rotate(-2deg);
    opacity: 0.3;
  }
  50% {
    transform: translateX(10%) rotate(2deg);
    opacity: 0.4;
  }
}

.animate-aurora {
  animation: aurora 20s ease-in-out infinite;
}

/* Float animations */
@keyframes float-slow {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -20px) scale(1.02);
  }
  66% {
    transform: translate(-20px, 10px) scale(0.98);
  }
}

@keyframes float-delayed {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  50% {
    transform: translate(-25px, -30px) scale(1.03);
  }
}

@keyframes float-reverse {
  0%, 100% {
    transform: translate(0, 0);
  }
  50% {
    transform: translate(20px, 15px);
  }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 30s ease-in-out infinite;
  animation-delay: -5s;
}

.animate-float-reverse {
  animation: float-reverse 20s ease-in-out infinite;
  animation-delay: -10s;
}
</style>
