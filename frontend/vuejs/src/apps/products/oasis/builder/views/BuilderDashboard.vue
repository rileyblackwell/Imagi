<!--
  BuilderDashboard.vue - Project Management Interface
  
  This component is responsible for:
  1. Creating new projects
  2. Deleting existing projects
  3. Listing all user projects
  4. Navigating to the workspace for editing
  
  It should NOT be responsible for:
  - Project file editing (handled by BuilderWorkspace.vue)
-->
<template>
  <BuilderLayout storage-key="builderDashboardSidebarCollapsed">
    <!-- Custom Sidebar Content with modern design -->
    <template #sidebar-content="{ collapsed }">
      <div class="p-4">
        <div class="mb-6">
          <div class="text-xs font-medium text-white/40 uppercase tracking-wider mb-3" v-if="!collapsed">
            Navigation
          </div>
          <ul class="space-y-1">
            <li v-for="item in navigationItems" :key="item.name">
              <router-link
                :to="item.to"
                class="group block px-3 py-2 rounded-xl transition-all duration-200 cursor-pointer"
                :class="[
                  isActiveRoute(item.to, item.exact) 
                    ? 'bg-gradient-to-r from-violet-500/15 to-fuchsia-500/15 text-violet-300 border border-violet-400/20' 
                    : 'hover:bg-white/[0.05] text-white/60 hover:text-white/90 border border-transparent hover:border-white/[0.08]'
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

    <!-- Premium Main Content - Matching Home Page -->
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
        <!-- Premium Header Section - Matching Home Page -->
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
                  <span class="text-sm font-medium text-white/70 tracking-wide">Project Workspace</span>
                </div>
              </div>
              
              <!-- Title with gradient text -->
              <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold tracking-tight mb-6 leading-[1.1]">
                <span class="block text-white/90">Create & Manage</span>
                <span class="block mt-2">
                  <span class="relative inline-block">
                    <span class="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-violet-400 bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-x">
                      Your Projects
                    </span>
                    <span class="absolute -bottom-2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-400/50 to-transparent"></span>
                  </span>
                </span>
              </h1>
              
              <!-- Description -->
              <p class="text-lg sm:text-xl text-white/50 mb-10 max-w-2xl mx-auto leading-relaxed">
                Leverage AI-powered tools to build web applications quickly. Start a new project or continue working on existing ones.
              </p>
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

        <!-- Authentication Error Message with Enhanced Styling -->
        <div v-if="showAuthError" class="px-6 sm:px-8 lg:px-12 pb-16">
          <div class="max-w-7xl mx-auto">
            <div class="relative group overflow-hidden">
              <!-- Animated Glow Effect -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
              
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-2xl border border-gray-800/60 p-10 text-center transition-all duration-500">
                <div class="w-20 h-20 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <i class="fas fa-lock text-4xl text-indigo-400 opacity-80"></i>
                </div>
                <h2 class="text-2xl font-semibold text-white mb-3">Authentication Required</h2>
                <p class="text-gray-300 mb-8 max-w-md mx-auto">Please log in to view and manage your projects.</p>
                <router-link 
                  to="/login" 
                  class="inline-flex items-center px-8 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl transform hover:-translate-y-1 transition-all duration-300 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30"
                >
                  <i class="fas fa-sign-in-alt mr-2.5"></i>
                  Log In
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Enhanced Project Section with Modern Layout -->
        <div v-else class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-7xl mx-auto">
            <div class="flex flex-col lg:flex-row gap-6 items-stretch">
              <!-- Project Create Section -->
              <div class="w-full lg:w-1/2 h-full flex flex-col">
                <!-- Premium glass card - Matching Home Page Style -->
                <div class="group relative h-full">
                  <!-- Background glow -->
                  <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden h-full flex flex-col">
                    <!-- Accent line -->
                    <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                    
                    <!-- Decorative elements -->
                    <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
                    <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  
                    <!-- Content -->
                    <div class="flex-1 p-6 md:p-8">
                      <!-- Header Section -->
                      <div class="relative z-10 mb-6">
                        <!-- Badge matching home page -->
                        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-4">
                          <i class="fas fa-plus text-xs text-violet-400/80"></i>
                          <span class="text-sm font-medium text-white/60">New Project</span>
                        </div>
                        
                        <!-- Title section -->
                        <div class="relative mb-4">
                          <h3 class="text-xl font-semibold text-white/90 leading-tight">Create a Project</h3>
                          <p class="text-white/50 text-sm mt-2 leading-relaxed">Build a new web application with AI assistance</p>
                        </div>
                      </div>
                      
                      <!-- Create Form -->
                      <div class="relative z-10">
                        <div class="flex flex-col space-y-5">
                          <!-- Project Name Input -->
                          <div class="relative group/input w-full">
                            <label class="block text-sm font-medium text-white/60 mb-2">Project Name</label>
                            <input
                              v-model="newProjectName"
                              type="text"
                              placeholder="Enter project name..."
                              class="w-full px-4 py-3.5 bg-white/[0.03] border border-white/[0.08] focus:border-violet-400/50 hover:border-white/[0.12] rounded-xl text-white/90 placeholder-white/30 transition-all duration-300 backdrop-blur-sm focus:bg-white/[0.05] disabled:opacity-50 disabled:cursor-not-allowed"
                              style="outline: none !important;"
                              :disabled="isCreating"
                            >
                          </div>
                          
                          <!-- Project Description Input -->
                          <div class="relative group/input w-full">
                            <label class="block text-sm font-medium text-white/60 mb-2">Description <span class="text-white/30">(optional)</span></label>
                            <textarea
                              v-model="newProjectDescription"
                              placeholder="Brief description of your project..."
                              class="w-full px-4 py-3.5 bg-white/[0.03] border border-white/[0.08] focus:border-violet-400/50 hover:border-white/[0.12] rounded-xl text-white/90 placeholder-white/30 transition-all duration-300 resize-none backdrop-blur-sm focus:bg-white/[0.05] disabled:opacity-50 disabled:cursor-not-allowed"
                              style="outline: none !important;"
                              :disabled="isCreating"
                              rows="2"
                            ></textarea>
                          </div>
                          
                          <!-- Create Button - Matching Home Page CTA -->
                          <div class="pt-2">
                            <button
                              @click="createProject"
                              :disabled="!newProjectName?.trim() || isCreating"
                              class="group/btn w-full inline-flex items-center justify-center gap-2 px-7 py-3.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300 hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:translate-y-0"
                            >
                              <template v-if="isCreating">
                                <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                <span>Creating...</span>
                              </template>
                              <template v-else>
                                <i class="fas fa-plus"></i>
                                <span>Create Project</span>
                                <i class="fas fa-arrow-right text-sm transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
                              </template>
                            </button>
                            
                            <p class="text-xs text-white/30 mt-4 text-center leading-relaxed flex items-center justify-center gap-1.5">
                              <i class="fas fa-info-circle text-violet-400/60"></i>
                              Project created with recommended starter template
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Project Library Section -->
              <div class="w-full lg:w-1/2 h-full flex flex-col">
                <!-- Premium glass card - Matching Home Page Style -->
                <div class="group relative h-full">
                  <!-- Background glow -->
                  <div class="absolute -inset-1 bg-gradient-to-r from-fuchsia-600/20 via-violet-600/20 to-fuchsia-600/20 rounded-3xl blur-xl opacity-40 group-hover:opacity-60 transition-opacity duration-500"></div>
                  
                  <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden h-full flex flex-col">
                    <!-- Accent line -->
                    <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent"></div>
                    
                    <!-- Decorative elements -->
                    <div class="absolute -bottom-20 -left-20 w-40 h-40 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
                    <div class="absolute -top-20 -right-20 w-32 h-32 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
                  
                    <!-- Content -->
                    <div class="flex-1 p-6 md:p-8 flex flex-col">
                      <!-- Header Section -->
                      <div class="relative z-10 mb-6">
                        <!-- Badge matching home page -->
                        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-4">
                          <i class="fas fa-folder text-xs text-fuchsia-400/80"></i>
                          <span class="text-sm font-medium text-white/60">Your Projects</span>
                        </div>
                        
                        <!-- Title section -->
                        <div class="relative mb-4">
                          <h3 class="text-xl font-semibold text-white/90 leading-tight">Project Library</h3>
                          <p class="text-white/50 text-sm mt-2 leading-relaxed">Continue working on your existing applications</p>
                        </div>
                      </div>

                    <!-- Search Input -->
                    <div class="relative z-10 mb-6">
                      <SearchInput 
                        v-model="searchQuery"
                        placeholder="Search projects"
                        variant="project"
                      />
                    </div>

                    <!-- Content Section -->
                    <div class="relative z-10 flex-1 flex flex-col overflow-hidden">
                      <!-- Loading State -->
                      <div v-if="isLoading" class="flex flex-col items-center justify-center py-12">
                        <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 mb-4">
                          <div class="w-6 h-6 border-2 border-violet-400/30 border-t-violet-400 rounded-full animate-spin"></div>
                        </div>
                        <p class="text-white/50 text-sm">Loading your projects...</p>
                      </div>

                      <!-- Error State -->
                      <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
                        <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-red-500/20 to-orange-500/20 border border-red-500/20 mb-4">
                          <i class="fas fa-exclamation-triangle text-red-400 text-xl"></i>
                        </div>
                        <p class="text-white/50 mb-4 text-center max-w-md text-sm">{{ error }}</p>
                        <div class="flex flex-col sm:flex-row gap-3">
                          <button
                            @click="retryFetch"
                            class="group/btn inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-xl text-white font-medium transition-all duration-300"
                          >
                            <i class="fas fa-redo text-sm"></i>
                            <span>Try Again</span>
                          </button>
                          
                          <button
                            @click="retryFetchWithDiagnostics"
                            class="group/btn inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-xl text-white font-medium shadow-lg shadow-violet-500/25 hover:shadow-xl hover:shadow-violet-500/30 transition-all duration-300"
                          >
                            <i class="fas fa-cog text-sm"></i>
                            <span>Diagnose</span>
                          </button>
                        </div>
                      </div>

                      <!-- No Search Results -->
                      <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="flex flex-col items-center justify-center py-12">
                        <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-white/10 to-white/5 border border-white/[0.08] mb-4">
                          <i class="fas fa-search text-white/40 text-xl"></i>
                        </div>
                        <h3 class="text-lg font-medium text-white/90 mb-1">No matching projects</h3>
                        <p class="text-white/50 text-center max-w-md text-sm">No projects found matching "{{ searchQuery }}"</p>
                      </div>

                      <!-- Empty State -->
                      <div v-else-if="!projects.length" class="flex flex-col items-center justify-center py-12">
                        <div class="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 mb-4">
                          <i class="fas fa-folder-open text-violet-400 text-xl"></i>
                        </div>
                        <h3 class="text-lg font-medium text-white/90 mb-1">No projects yet</h3>
                        <p class="text-white/50 text-center max-w-md mb-4 text-sm">Create your first project to start building with Imagi</p>
                        
                        <!-- Directional hint -->
                        <div class="flex items-center text-violet-400 text-sm">
                          <i class="fas fa-arrow-left mr-2 animate-pulse"></i>
                          <span>Get started with a new project</span>
                        </div>
                      </div>

                      <!-- Projects Display -->
                      <div v-else-if="displayedProjects.length > 0" class="flex-1 flex flex-col overflow-hidden">
                        <!-- Project count badge -->
                        <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] rounded-full border border-white/[0.08] mb-4 self-start">
                          <i class="fas fa-clock text-xs text-fuchsia-400/80"></i>
                          <span class="text-sm font-medium text-white/60">
                            {{ searchQuery ? `${displayedProjects.length} Results` : `${projects.length || 0} Projects` }}
                          </span>
                        </div>
                        
                        <!-- Scrollable Project Cards Container -->
                        <div class="flex-1 overflow-y-auto pr-2 space-y-4 custom-scrollbar">
                          <ProjectCard
                            v-for="project in displayedProjects"
                            :key="project.id"
                            :project="project"
                            @delete="confirmDelete"
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
    </div>
  </div>
  </BuilderLayout>
</template>

<script setup lang="ts">


import { ref, computed, watch, onBeforeUnmount, onMounted, onActivated, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { ProjectCard } from '@/apps/products/oasis/builder/components/molecules'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '../composables/useConfirm'
import { useNotificationStore } from '@/shared/stores/notificationStore'
import { SearchInput } from '../components/atoms'
import { useProjectSearch } from '../composables/useProjectSearch'
import type { Project } from '../types/components' 
import { normalizeProject } from '../types/components' // Use the normalizeProject from components.ts
import { ProjectService } from '../services/projectService'


const router = useRouter()
const route = useRoute()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const { showNotification } = useNotification()
const { confirm } = useConfirm()
const notificationStore = useNotificationStore()

// State with types - remove searchQuery since it's handled in ProjectList
const newProjectName = ref('')
const newProjectDescription = ref('') // New ref for project description
const isCreating = ref(false)
const isInitializing = ref(true) // Added to track initialization state

// Computed with types - remove filteredProjects
const projects = computed(() => projectStore.projects)
// Add a normalized projects computed property that ensures all projects have the required status field
// Ensure normalizedProjects always returns an array of Project with all required fields (including created_at)
const normalizedProjects = computed<Project[]>(() => {
  if (!projects.value) return [];
  return projects.value.map(project => {
    // normalizeProject already ensures created_at is set with fallbacks
    return normalizeProject(project);
  });
})
const isLoading = computed(() => projectStore.loading || isInitializing.value)
const error = computed(() => projectStore.error || '')
const showAuthError = computed(() => !authStore.isAuthenticated && !isLoading.value)

// Use project search composable with options to include descriptions in search
const { searchQuery, filteredProjects } = useProjectSearch(normalizedProjects, { includeDescription: true });



// Compute displayed projects - show search results if searching, otherwise show 3 most recent
// Also filter out any projects that are in the deleted list
const displayedProjects = computed<Project[]>(() => {
  // Get deleted projects list for filtering
  let deletedProjects: string[] = [];
  try {
    deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]');
  } catch (e) {
    // Handle localStorage errors silently
  }
  
  // Check if we have a meaningful search query (not just whitespace)
  const hasSearchQuery = searchQuery.value?.trim().length > 0;
  
  let baseProjects: Project[] = [];
  
  if (hasSearchQuery) {
    // Return filtered search results
    baseProjects = filteredProjects.value || [];
  } else {
    // Show all projects when not searching (projects page removed)
    if (!normalizedProjects.value?.length) {
      return [];
    }
    
    baseProjects = [...normalizedProjects.value]
      .sort((a, b) => {
        // Handle cases where updated_at might be undefined
        if (!a.updated_at) return 1;  // If a's date is missing, b comes first
        if (!b.updated_at) return -1; // If b's date is missing, a comes first
        
        const dateA = new Date(a.updated_at).getTime()
        const dateB = new Date(b.updated_at).getTime()
        return dateB - dateA
      })
  }
  
  // Filter out deleted projects to prevent UI issues
  return baseProjects.filter(project => 
    project && project.id && !deletedProjects.includes(String(project.id))
  );
});

// Navigation items
const navigationItems = [
  {
    name: 'Builder',
    to: '/products/oasis/builder/dashboard',
    icon: 'fas fa-hammer',
    exact: true
  },
  {
    name: 'Purchase AI Credits',
    to: '/payments/checkout',
    icon: 'fas fa-money-bill-wave',
    exact: true
  }
];

// Check if a route is active (exact match or starts with path for nested routes)
const isActiveRoute = (path: string, exact?: boolean): boolean => {
  if (exact) {
    return route.path === path
  }
  return route.path.startsWith(path)
}

/**
 * Create a new project
 */
async function createProject() {
  if (!authStore.isAuthenticated) {
    showNotification({
      message: 'Please log in to create projects',
      type: 'error'
    })
    return
  }
  
  // Validate project name
  if (!newProjectName.value.trim()) {
    showNotification({
      message: 'Project name cannot be empty',
      type: 'error'
    })
    return
  }
  
  isCreating.value = true
  
  try {
    // Create a properly formatted project data object with name and description
    const projectData = {
      name: newProjectName.value.trim(),
      description: newProjectDescription.value.trim() // Use the description value
    }
    
    const newProject = await projectStore.createProject(projectData)
    
    // Clear the project name and description fields after successful creation
    newProjectName.value = ''
    newProjectDescription.value = ''
    
    // Log project information to debug any ID issues
    console.debug('Created project details:', {
      project: newProject,
      id: newProject.id,
      idType: typeof newProject.id
    })
    
    // Show success notification
    showNotification({
      message: `Project "${newProject.name}" created successfully! Opening workspace...`,
      type: 'success',
      duration: 3000
    })
    
    // Force refresh projects list after creation
    // Use nextTick to ensure the UI updates before refreshing
    await nextTick()
    try {
      await fetchProjects(true) // Use the local fetch function which ensures proper state updates
    } catch (refreshError) {
      console.warn('Failed to refresh projects after creation:', refreshError)
    }
    
    // Navigate to the workspace for the newly created project
    // Give a brief moment for the success notification to be seen
    setTimeout(() => {
      router.push({ 
        name: 'builder-workspace', 
        params: { projectId: String(newProject.id) } 
      })
    }, 1500)
    
  } catch (error: any) {
    showNotification({
      message: error?.message || 'Failed to create project',
      type: 'error'
    })
  } finally {
    isCreating.value = false
  }
}

/**
 * Load/reload the projects list
 * This is the ONLY place that should handle loading the list of all projects
 */
const fetchProjects = async (force = false) => {
  if (!authStore.isAuthenticated) {
    isInitializing.value = false
    return
  }
  
  try {
    // First, ensure project store auth state is synchronized
    if (projectStore.isAuthenticated !== authStore.isAuthenticated) {
      projectStore.setAuthenticated(authStore.isAuthenticated)
    }
    
    await projectStore.fetchProjects(force)
    
  } catch (error: any) {
    console.error('Error fetching projects:', error)
    showNotification({
      message: error?.message || 'Failed to load projects',
      type: 'error'
    })
  } finally {
    isInitializing.value = false
  }
}

/**
 * Retry fetching projects if there was an error
 */
const retryFetch = () => {
  projectStore.clearError()
  fetchProjects(true) // Force refresh when retrying
}

/**
 * Confirm and delete a project
 * This is the ONLY place in the application that should call projectStore.deleteProject
 */
const confirmDelete = async (project: Project) => {
  if (!authStore.isAuthenticated) {
    showNotification({
      message: 'Please log in to delete projects',
      type: 'error'
    })
    return
  }
  
  // Use confirm dialog
  const confirmed = await confirm({
    title: 'Delete Project',
    message: `Are you sure you want to delete "${project.name}"? This action cannot be undone.`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })
  
  if (!confirmed) {
    return
  }
  
  // Capture the project name before deletion to ensure we have it for the notification
  const projectName = project.name || `Project ${project.id}` || 'Unknown Project'
  
  // Check if user is currently in the workspace for this project
  const isCurrentlyInWorkspace = router.currentRoute.value.name === 'builder-workspace' && 
                                 router.currentRoute.value.params.projectId === String(project.id)
  
  try {
    // First clear the cache to ensure fresh data
    projectStore.clearProjectsCache()
    
    // Mark project as deleted BEFORE making the API call to prevent race conditions
    const deletedProjectId = String(project.id)
    
    // Add to deleted projects list immediately to prevent any fetching attempts
    try {
      const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
      if (!deletedProjects.includes(deletedProjectId)) {
        deletedProjects.push(deletedProjectId)
        localStorage.setItem('deletedProjects', JSON.stringify(deletedProjects))
        
        // Also store timestamp for cleanup purposes
        const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
        deletedProjectsTimestamp[deletedProjectId] = Date.now()
        localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
      }
    } catch (e) {
      console.error('Failed to store deleted project ID in localStorage:', e)
    }
    
    await projectStore.deleteProject(String(project.id))
    
    // If user was in the workspace for this project, navigate away from it
    if (isCurrentlyInWorkspace) {
      console.log('User was in workspace for deleted project, redirecting to dashboard')
      await router.push({ name: 'builder-dashboard' })
    }
    
    // Immediately refresh the projects list to show updated state
    try {
      await fetchProjects(true) // Force refresh to get latest state from API
    } catch (refreshError) {
      console.warn('Failed to refresh projects after deletion:', refreshError)
    }
    
    // Show success notification with captured project name
    showNotification({
      type: 'success',
      message: `"${projectName}" deleted successfully`,
      duration: 4000
    })

  } catch (error: any) {
    console.error('Error deleting project:', error)
    
    // Check if the error is actually a success (project was deleted but API returned unexpected response)
    if (error.response?.status === 404) {
      // Project is gone, which means deletion was successful
      // Clear cache and refresh
      projectStore.clearProjectsCache()
      

      
      // If user was in the workspace for this project, navigate away from it
      if (isCurrentlyInWorkspace) {
        console.log('Project was deleted (404), redirecting from workspace to dashboard')
        await router.push({ name: 'builder-dashboard' })
      }
      
            // Still refresh the projects list to ensure clean state
      try {
        await fetchProjects(true)
      } catch (refreshError) {
        console.warn('Failed to refresh projects after deletion:', refreshError)
      }
      
      // Show success notification with captured project name
      showNotification({
        type: 'success',
        message: `"${projectName}" deleted successfully`,
        duration: 4000
      })    } else {
      // Actual error occurred - remove the project from deleted list if it was added
      try {
        const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
        const updatedDeletedProjects = deletedProjects.filter((id: string) => id !== String(project.id))
        localStorage.setItem('deletedProjects', JSON.stringify(updatedDeletedProjects))
        
        // Also remove timestamp
        const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
        delete deletedProjectsTimestamp[String(project.id)]
        localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
      } catch (e) {
        console.warn('Failed to remove project from deleted list after error:', e)
      }
      
              // Show actual error with captured project name
        showNotification({
          message: error?.message || `Failed to delete "${projectName}"`,
          type: 'error',
          duration: 5000
        })
    }
  }
}

/**
 * Enhanced debug function to diagnose project loading issues
 */
const retryFetchWithDiagnostics = async () => {
  console.debug('Running diagnostic fetch...')
  
  try {
    const diagnostics = await ProjectService.runDiagnostics()
    
    console.debug('Diagnostics completed:', diagnostics)
    
    // If diagnostics found projects, update the store
    if (diagnostics.success && diagnostics.details.connectionTest?.projects) {
      projectStore.updateProjects(diagnostics.details.connectionTest.projects)
    }
    
    // Force a fetch after diagnostics
    fetchProjects(true)
  } catch (error) {
    console.error('Diagnostics failed:', error)
    // Still try to fetch projects as fallback
    fetchProjects(true)
  }
}

/**
 * Synchronize the auth state between global auth store and project store
 * to ensure consistency
 */
const synchronizeStores = async () => {
  try {
    // Only force auth initialization if really needed and not recently done
    // Let the auth store handle its own caching logic
    if (!authStore.initialized) {
      await authStore.initAuth()
    }
    
    // Wait to ensure auth store is completely initialized
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Sync project store auth state with auth store
    projectStore.setAuthenticated(authStore.isAuthenticated)
    
    // Let auth store handle token validation if needed
    if (!authStore.isAuthenticated && !authStore.initialized) {
      try {
        await authStore.validateAuth()
      } catch (validationError) {
        // Handle error silently
      }
    }
  } catch (error) {
    // Handle error silently
  } finally {
    // If still not authenticated, make sure isInitializing is set to false
    if (!authStore.isAuthenticated) {
      isInitializing.value = false
    }
  }
}

/**
 * Force refresh projects (used by refresh button)
 */
const refreshProjects = async () => {
  try {
    showNotification({
      type: 'info',
      message: 'Refreshing projects...'
    })
    
    await fetchProjects(true) // Force refresh
    
    showNotification({
      type: 'success',
      message: 'Projects refreshed successfully'
    })
  } catch (error) {
    showNotification({
      type: 'error',
      message: 'Failed to refresh projects'
    })
  }
}

// Set up watchers and lifecycle hooks
onMounted(async () => {
  console.debug('BuilderDashboard mounted')
  
  // Always force refresh projects when the dashboard loads to ensure we have the latest data
  try {
    console.debug('Forcing refresh of projects on dashboard load')
    // Force refresh to always get the latest projects from API
    await fetchProjects(true)
  } catch (error) {
    console.error('Initial project fetch failed:', error)
    
    // Wait a moment and try again if authentication is confirmed
    if (authStore.isAuthenticated) {
      setTimeout(async () => {
        try {
          console.debug('Retrying project fetch after initial failure')
          await fetchProjects(true) // Force on retry after failure
        } catch (retryError) {
          console.error('Retry fetch also failed:', retryError)
        }
      }, 2000)
    }
  }
})

// Add support for keep-alive to refresh when component is re-activated
onActivated(async () => {
  console.debug('BuilderDashboard activated - refreshing projects from API')
  if (authStore.isAuthenticated) {
    // Always force refresh projects when the component is activated (tab switch, navigation back, etc.)
    try {
      await fetchProjects(true) // Always force refresh to get latest state from API
    } catch (error) {
      console.error('Failed to refresh projects on activation:', error)
    }
  }
})

// Clean up resources when leaving the dashboard
onBeforeUnmount(() => {
  // Clear dashboard-specific notifications when leaving
  const notificationStore = useNotificationStore()
  notificationStore.clear()
})

// Watch auth store authentication status
watch(
  () => authStore.isAuthenticated,
  (newAuthStatus) => {
    console.debug('Auth state changed:', newAuthStatus)
    if (newAuthStatus) {
      // Don't automatically fetch projects when auth state changes
      // Projects will be fetched when needed by the component's normal flow
      // This prevents unnecessary API calls immediately after login
    }
  }
)
</script>

<style scoped>
/* Remove browser default styling for form inputs */
input, textarea {
  outline: none !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus, textarea:focus {
  outline: none !important;
  box-shadow: none !important;
}

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

/* Premium scrollbar */
:deep(::-webkit-scrollbar) {
  width: 6px;
}

:deep(::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.02);
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(139, 92, 246, 0.5);
}

/* Custom scrollbar for project list */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.02);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 92, 246, 0.5);
}
</style>