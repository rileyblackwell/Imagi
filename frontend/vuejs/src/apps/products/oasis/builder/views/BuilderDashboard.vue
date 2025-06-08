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
  <BuilderLayout 
    storage-key="builderDashboardSidebarCollapsed"
    :navigation-items="navigationItems"
  >
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
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">PROJECT WORKSPACE</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h2 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Create & Manage</span> 
                  <br class="hidden sm:block" />Your Projects
                </h2>
                
                <!-- Enhanced Description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  Leverage AI-powered tools to build web applications quickly. Start a new project or continue working on existing ones.
                </p>
              </div>
              
              <!-- Stats Overview Cards -->
              <div class="flex flex-wrap gap-4 justify-end">
                <!-- Project count moved to Project Library -->
              </div>
            </div>
            
            <!-- Animated Divider Line -->
            <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent my-12 animate-pulse-slow"></div>
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
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-3xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full flex flex-col">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50"></div>
                  
                  <!-- Content with reduced padding for slender look -->
                  <div class="flex-1 p-6">
                    <!-- Sleek Header Section -->
                    <div class="relative z-10 mb-6">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-3 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">New Project</span>
                      </div>
                      
                      <!-- Elegant title section -->
                      <div class="relative mb-4 text-center">
                        <h3 class="text-xl font-semibold text-white leading-tight">Create a Project</h3>
                        <p class="text-gray-400 text-sm mt-1 leading-relaxed">Build a new web application with AI assistance</p>
                      </div>
                    </div>
                    
                    <!-- Sleek Create Form -->
                    <div class="relative z-10">
                      <div class="flex flex-col space-y-4">
                        <!-- Modern Project Name Input -->
                        <div class="relative group/input w-full">
                          <!-- Enhanced glow effect on focus -->
                          <div class="absolute inset-0 bg-gradient-to-r from-violet-500/12 to-indigo-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
                          
                          <label class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Project Name</label>
                          <input
                            v-model="newProjectName"
                            type="text"
                            placeholder="Enter project name..."
                            class="relative z-10 w-full px-4 py-3 bg-white/5 border border-white/10 focus:border-violet-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-violet-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                            style="outline: none !important; box-shadow: none !important;"
                            :disabled="isCreating"
                          >
                        </div>
                        
                        <!-- Modern Project Description Input -->
                        <div class="relative group/input w-full">
                          <!-- Enhanced glow effect on focus -->
                          <div class="absolute inset-0 bg-gradient-to-r from-violet-500/12 to-indigo-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
                          
                          <label class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Description <span class="text-gray-500 normal-case">(optional)</span></label>
                          <textarea
                            v-model="newProjectDescription"
                            placeholder="Brief description of your project..."
                            class="relative z-10 w-full px-4 py-3 bg-white/5 border border-white/10 focus:border-violet-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 resize-none backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-violet-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
                            style="outline: none !important; box-shadow: none !important;"
                            :disabled="isCreating"
                            rows="2"
                          ></textarea>
                        </div>
                        
                        <!-- Sleek Create Button -->
                        <div class="pt-1">
                          <button
                            @click="createProject"
                            :disabled="!newProjectName?.trim() || isCreating"
                            class="w-full px-4 py-2.5 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            
                            <span class="relative flex items-center justify-center">
                              <template v-if="isCreating">
                                <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                                Creating...
                              </template>
                              <template v-else>
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                                </svg>
                                Create Project
                              </template>
                            </span>
                          </button>
                          
                          <p class="text-xs text-gray-500 mt-3 text-center leading-relaxed">
                            <svg class="w-3 h-3 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                            </svg>
                            Project created with recommended starter template
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Project Library Section -->
              <div class="w-full lg:w-1/2 h-full flex flex-col">
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-3xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full flex flex-col">
                  <!-- Sleek gradient header -->
                  <div class="h-1 w-full bg-gradient-to-r from-violet-400 via-indigo-400 to-violet-400 opacity-80"></div>
                  
                  <!-- Subtle background effects -->
                  <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-violet-400/4 to-indigo-400/4 rounded-full blur-3xl opacity-50"></div>
                  
                  <!-- Content with reduced padding for slender look -->
                  <div class="flex-1 p-6">
                    <!-- Sleek Header Section -->
                    <div class="relative z-10 mb-6">
                      <!-- Modern pill badge -->
                      <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-violet-500/15 to-indigo-500/15 border border-violet-400/20 rounded-full mb-3 backdrop-blur-sm">
                        <div class="w-1.5 h-1.5 bg-violet-400 rounded-full mr-2 animate-pulse"></div>
                        <span class="text-violet-300 font-medium text-xs tracking-wide uppercase">Your Projects</span>
                      </div>
                      
                      <!-- Elegant title section with stats in corner -->
                      <div class="relative mb-4">
                        <!-- Total Projects in top right corner -->
                        <div class="absolute top-0 right-0">
                          <div class="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-2 flex items-center gap-2">
                            <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-400/20 to-indigo-400/20 flex items-center justify-center border border-violet-400/20">
                              <svg class="w-3 h-3 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                              </svg>
                            </div>
                            <div>
                              <p class="text-xs text-gray-400 leading-none">{{ projects.length || 0 }}</p>
                            </div>
                          </div>
                        </div>
                        
                        <h3 class="text-xl font-semibold text-white leading-tight pr-20 text-center">Project Library</h3>
                        <p class="text-gray-400 text-sm mt-1 leading-relaxed text-center">Continue working on your existing applications</p>
                      </div>
                      
                      <!-- Modern Search Input -->
                      <div class="mb-4 flex justify-center">
                        <div class="w-full max-w-md">
                          <ProjectSearchInput 
                            v-model="searchQuery"
                            placeholder="Search projects"
                          />
                        </div>
                      </div>
                    </div>

                    <!-- Modern Content Section -->
                    <div class="relative z-10">
                      <!-- Sleek Loading State -->
                    <div v-if="isLoading" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-gradient-to-br from-violet-400/20 to-indigo-400/20 rounded-2xl flex items-center justify-center mb-4 border border-violet-400/20">
                        <div class="w-5 h-5 border-2 border-violet-400/30 border-t-violet-400 rounded-full animate-spin"></div>
                      </div>
                      <p class="text-gray-400 text-sm">Loading your projects...</p>
                    </div>

                    <!-- Sleek Error State -->
                    <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-gradient-to-br from-red-400/20 to-orange-400/20 rounded-2xl flex items-center justify-center mb-4 border border-red-400/20">
                        <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                      </div>
                      <p class="text-gray-400 mb-4 text-center max-w-md text-sm">{{ error }}</p>
                      <div class="flex flex-col sm:flex-row gap-2">
                        <button
                          @click="retryFetch"
                          class="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-indigo-400/30 text-white rounded-xl transition-all duration-300 inline-flex items-center text-sm"
                        >
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                          </svg>
                          Try Again
                        </button>
                        
                        <button
                          @click="retryFetchWithDiagnostics"
                          class="px-4 py-2 bg-gradient-to-r from-indigo-500/80 to-violet-500/80 hover:from-indigo-400 hover:to-violet-400 text-white rounded-xl transition-all duration-300 inline-flex items-center text-sm"
                        >
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          </svg>
                          Diagnose
                        </button>
                      </div>
                    </div>

                    <!-- Sleek No Search Results -->
                    <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-gradient-to-br from-gray-400/20 to-gray-600/20 rounded-2xl flex items-center justify-center mb-4 border border-gray-400/20">
                        <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                        </svg>
                      </div>
                      <h3 class="text-lg font-medium text-white mb-1">No matching projects</h3>
                      <p class="text-gray-400 text-center max-w-md text-sm">No projects found matching "{{ searchQuery }}"</p>
                    </div>

                    <!-- Sleek Empty State -->
                    <div v-else-if="!projects.length" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-gradient-to-br from-violet-400/20 to-indigo-400/20 rounded-2xl flex items-center justify-center mb-4 border border-violet-400/20">
                        <svg class="w-5 h-5 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                        </svg>
                      </div>
                      <h3 class="text-lg font-medium text-white mb-1">No projects yet</h3>
                      <p class="text-gray-400 text-center max-w-md mb-4 text-sm">Create your first project to start building with Imagi</p>
                      
                      <!-- Elegant directional hint -->
                      <div class="flex items-center text-violet-400 text-sm">
                        <svg class="w-4 h-4 mr-2 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                        </svg>
                        <span>Get started with a new project</span>
                      </div>
                    </div>

                    <!-- Sleek Projects Display -->
                    <div v-else-if="displayedProjects.length > 0">
                      <div class="flex items-center bg-gradient-to-r from-violet-400/8 to-indigo-400/8 rounded-2xl px-3 py-2 mb-4 border border-violet-400/15">
                        <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-400/20 to-indigo-400/20 flex items-center justify-center mr-2 border border-violet-400/20">
                          <svg class="w-3 h-3 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                        </div>
                        <h3 class="text-xs font-medium text-violet-300 uppercase tracking-wider">
                          {{ searchQuery ? `Search Results (${displayedProjects.length})` : 'Recently Opened' }}
                        </h3>
                      </div>
                      
                      <!-- Project Cards with modern spacing -->
                      <div class="space-y-4">
                        <ProjectCard
                          v-for="project in displayedProjects"
                          :key="project.id"
                          :project="project"
                          @delete="confirmDelete"
                        />
                      </div>
                      
                      <!-- Sleek View All Link -->
                      <div v-if="!searchQuery && projects.length > 3" class="mt-6 text-center">
                        <router-link
                          to="/products/oasis/builder/projects"
                          class="inline-flex items-center px-4 py-2 bg-white/5 hover:bg-white/8 border border-white/10 text-gray-400 hover:text-gray-300 rounded-xl transition-all duration-200 text-sm"
                        >
                          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                          </svg>
                          View All Projects ({{ projects.length }})
                        </router-link>
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
import { useRouter } from 'vue-router'
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { ProjectCard } from '@/apps/products/oasis/builder/components/molecules'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '../composables/useConfirm'
import { useNotificationStore } from '@/shared/stores/notificationStore'
import ProjectSearchInput from '../components/atoms/ProjectSearchInput.vue'
import { useProjectSearch } from '../composables/useProjectSearch'
import type { Project } from '../types/components' 
import { normalizeProject } from '../types/components' // Use the normalizeProject from components.ts
import { ProjectService } from '../services/projectService'


const router = useRouter()
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
    // Show 3 most recently updated projects when not searching
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
      .slice(0, 3);
  }
  
  // Filter out deleted projects to prevent UI issues
  return baseProjects.filter(project => 
    project && project.id && !deletedProjects.includes(String(project.id))
  );
});

// Navigation items
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
/* Completely remove any browser default styling for form inputs */
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

.delay-700 {
  animation-delay: 700ms;
}

/* Custom scrollbar styling for project container */
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
  background: theme('colors.gray.700');
  border-radius: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: theme('colors.gray.600');
}
</style>