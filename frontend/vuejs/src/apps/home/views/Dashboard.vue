<template>
  <DashboardLayout :navigationItems="navigationItems">
    <div class="flex flex-col w-full min-h-screen bg-dark-900 relative overflow-hidden">
      <!-- Enhanced Background Effects -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Refined gradient background with improved colors matching Imagi brand -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary-600/10 via-indigo-500/5 to-violet-600/10"></div>
        
        <!-- Ambient glow effects with subtle pulsing animation -->
        <div class="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[800px] bg-gradient-to-r from-primary-600/15 to-violet-600/15 rounded-full blur-[120px] opacity-40 animate-pulse-slow"></div>
        <div class="absolute bottom-0 right-0 w-[600px] h-[600px] bg-gradient-to-r from-indigo-600/10 to-primary-600/10 rounded-full blur-[100px] opacity-30"></div>
        
        <!-- Enhanced subtle grid pattern -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02] mix-blend-overlay"></div>
      </div>

      <!-- Dashboard Content with improved spacing and organization -->
      <div class="relative z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
          <!-- Welcome Section with Enhanced Imagi Title Styling -->
          <div class="mb-10">
            <!-- Imagi Title with improved glow and animation -->
            <div class="inline-flex items-center justify-center mb-8">
              <div class="rounded-2xl bg-gradient-to-br p-[1.5px] from-primary-400/50 to-violet-400/50
                        hover:from-primary-300/60 hover:to-violet-300/60 transition-all duration-300">
                <div class="px-8 py-4 rounded-2xl bg-dark-800/95 backdrop-blur-xl
                          shadow-[0_0_25px_-5px_rgba(99,102,241,0.5)]">
                  <h1 class="text-4xl font-bold bg-gradient-to-r from-pink-300 via-emerald-300 to-yellow-200 
                            bg-clip-text text-transparent tracking-tight
                            drop-shadow-[0_0_15px_rgba(236,72,153,0.3)]
                            animate-gradient">
                    Imagi
                  </h1>
                </div>
              </div>
            </div>
            
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <h2 class="text-3xl font-bold text-white mb-3 tracking-tight">
                  Welcome back, {{ authStore.user?.name || 'Developer' }}! 👋
                </h2>
                <p class="text-lg text-gray-300/90 max-w-2xl leading-relaxed">
                  Here's what's happening with your projects today.
                </p>
              </div>
              <button
                @click="$router.push({ name: 'builder-new-project' })"
                class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-600 to-violet-600 text-white rounded-xl hover:from-primary-700 hover:to-violet-700 shadow-lg shadow-primary-600/30 hover:shadow-primary-600/40 transform hover:translate-y-[-2px] transition-all duration-300 self-start"
              >
                <i class="fas fa-plus mr-2.5"></i>
                New Project
              </button>
            </div>
          </div>

          <!-- Stats Overview with Enhanced Cards and Consistent Styling -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-10">
            <div 
              v-for="stat in statsData" 
              :key="stat.title"
              class="group relative transform transition-all duration-300 hover:translate-y-[-3px]"
            >
              <!-- Enhanced hover glow effect with improved colors -->
              <div class="absolute -inset-[1px] rounded-xl bg-gradient-to-r opacity-0 group-hover:opacity-100 blur-[2px] transition-all duration-300" 
                :class="{
                  'from-primary-600/30 via-violet-600/30 to-indigo-600/30': stat.color === 'primary',
                  'from-green-600/30 via-emerald-600/30 to-teal-600/30': stat.color === 'success',
                  'from-yellow-600/30 via-amber-600/30 to-orange-600/30': stat.color === 'warning',
                  'from-blue-600/30 via-sky-600/30 to-cyan-600/30': stat.color === 'info'
                }"
              ></div>
              
              <!-- Card content with enhanced styling and consistent brand colors -->
              <div class="relative bg-dark-800/80 backdrop-blur-md rounded-xl p-6 border border-dark-700/80 group-hover:border-primary-600/30 transition-all duration-300 shadow-lg shadow-dark-950/40 group-hover:shadow-xl group-hover:shadow-primary-600/15 h-full">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-lg font-medium text-gray-300">{{ stat.title }}</h3>
                  <div class="w-10 h-10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-all duration-300"
                    :class="{
                      'bg-primary-600/15 text-primary-400': stat.color === 'primary',
                      'bg-green-600/15 text-green-400': stat.color === 'success',
                      'bg-yellow-600/15 text-yellow-400': stat.color === 'warning',
                      'bg-blue-600/15 text-blue-400': stat.color === 'info'
                    }"
                  >
                    <i :class="[stat.icon, 'text-lg']"></i>
                  </div>
                </div>
                <div class="flex items-end justify-between">
                  <div class="text-3xl font-bold text-white">{{ stat.value }}</div>
                  <div class="text-sm font-medium"
                    :class="{
                      'text-green-400': stat.trend.startsWith('+'),
                      'text-red-400': stat.trend.startsWith('-')
                    }"
                  >
                    {{ stat.trend }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Main Grid with Enhanced Cards -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Projects & Activity Column -->
            <div class="lg:col-span-2 space-y-8">
              <!-- Recent Projects -->
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-primary-500/30 transition-all duration-300 shadow-lg shadow-dark-950/20 hover:shadow-xl hover:shadow-primary-500/10">
                <div class="flex items-center justify-between mb-6">
                  <div class="flex items-center gap-4">
                    <div class="w-12 h-12 bg-gradient-to-br from-primary-500 to-violet-500 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/20 transform hover:scale-105 transition-all duration-300">
                      <i class="fas fa-folder-open text-xl text-white"></i>
                    </div>
                    <h2 class="text-xl font-bold text-white">Recent Projects</h2>
                  </div>
                  <router-link 
                    to="/products/oasis/builder/projects"
                    class="text-primary-400 hover:text-primary-300 transition-colors text-sm font-medium flex items-center"
                  >
                    View All
                    <i class="fas fa-arrow-right ml-2"></i>
                  </router-link>
                </div>
                
                <div class="space-y-4">
                  <div 
                    v-for="project in recentProjects"
                    :key="project.id"
                    class="group bg-dark-900/50 hover:bg-dark-900/80 border border-dark-700/50 hover:border-primary-500/30 rounded-xl p-4 transition-all duration-300 transform hover:translate-y-[-2px] cursor-pointer"
                    @click="goToProject(project.id)"
                  >
                    <div class="flex items-center justify-between">
                      <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20">
                          <i class="fas fa-cube text-primary-400"></i>
                        </div>
                        <div>
                          <h3 class="text-white font-medium group-hover:text-primary-400 transition-colors">{{ project.name }}</h3>
                          <p class="text-gray-400 text-sm">Last updated {{ formatDate(project.updated_at) }}</p>
                        </div>
                      </div>
                      <div class="text-primary-400 opacity-0 group-hover:opacity-100 transition-opacity">
                        <i class="fas fa-arrow-right"></i>
                      </div>
                    </div>
                  </div>
                  
                  <div v-if="!recentProjects.length" class="flex flex-col items-center justify-center py-10 bg-dark-900/30 rounded-xl border border-dark-700/50">
                    <i class="fas fa-folder-open text-3xl text-gray-500 mb-3 opacity-50"></i>
                    <p class="text-gray-400 text-center">No projects yet. Create your first project to get started!</p>
                    <button
                      @click="$router.push({ name: 'builder-new-project' })"
                      class="mt-4 px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg hover:bg-primary-500/30 transition-colors"
                    >
                      <i class="fas fa-plus mr-2"></i>
                      Create Project
                    </button>
                  </div>
                </div>
              </div>

              <!-- Recent Activity -->
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-primary-500/30 transition-all duration-300 shadow-lg shadow-dark-950/20 hover:shadow-xl hover:shadow-primary-500/10">
                <div class="flex items-center gap-4 mb-6">
                  <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 transform hover:scale-105 transition-all duration-300">
                    <i class="fas fa-history text-xl text-white"></i>
                  </div>
                  <h2 class="text-xl font-bold text-white">Activity Feed</h2>
                </div>
                
                <ActivityFeed :activities="recentActivities" />
              </div>
            </div>

            <!-- Quick Actions & Resources Column -->
            <div class="space-y-8">
              <!-- Quick Actions -->
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-primary-500/30 transition-all duration-300 shadow-lg shadow-dark-950/20 hover:shadow-xl hover:shadow-primary-500/10">
                <div class="flex items-center gap-4 mb-6">
                  <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 transform hover:scale-105 transition-all duration-300">
                    <i class="fas fa-bolt text-xl text-white"></i>
                  </div>
                  <h2 class="text-xl font-bold text-white">Quick Actions</h2>
                </div>
                
                <div class="space-y-3">
                  <button
                    v-for="action in quickActions"
                    :key="action.title"
                    @click="$router.push(action.route)"
                    class="w-full flex items-center justify-between p-4 bg-dark-900/50 hover:bg-dark-900/80 border border-dark-700/50 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:translate-y-[-2px] text-white hover:text-primary-400 group"
                  >
                    <div class="flex items-center gap-3">
                      <div class="w-8 h-8 rounded-lg bg-primary-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
                        <i :class="[action.icon, 'text-primary-400']"></i>
                      </div>
                      <span>{{ action.title }}</span>
                    </div>
                    <i class="fas fa-chevron-right text-gray-500 group-hover:text-primary-400 transition-colors"></i>
                  </button>
                </div>
              </div>

              <!-- Available Credits -->
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-primary-500/30 transition-all duration-300 shadow-lg shadow-dark-950/20 hover:shadow-xl hover:shadow-primary-500/10">
                <div class="flex items-center gap-4 mb-6">
                  <div class="w-12 h-12 bg-gradient-to-br from-amber-500 to-yellow-500 rounded-xl flex items-center justify-center shadow-lg shadow-amber-500/20 transform hover:scale-105 transition-all duration-300">
                    <i class="fas fa-coins text-xl text-white"></i>
                  </div>
                  <h2 class="text-xl font-bold text-white">Credits Overview</h2>
                </div>
                
                <div class="text-center p-4">
                  <div class="text-4xl font-bold bg-gradient-to-r from-amber-400 to-yellow-300 bg-clip-text text-transparent mb-3">
                    {{ credits }}
                  </div>
                  <p class="text-gray-300 mb-6">Available Credits</p>
                  <div class="relative h-3 bg-dark-900/70 rounded-full overflow-hidden mb-6">
                    <div 
                      class="absolute top-0 left-0 h-full bg-gradient-to-r from-amber-500 to-yellow-500 rounded-full"
                      :style="{ width: `${(creditsUsed / creditsPlan) * 100}%` }"
                    ></div>
                  </div>
                  <router-link 
                    to="/payments"
                    class="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-amber-500 to-yellow-500 text-white rounded-xl hover:from-amber-600 hover:to-yellow-600 shadow-lg shadow-amber-500/20 hover:shadow-amber-500/30 transform hover:translate-y-[-2px] transition-all duration-300"
                  >
                    <i class="fas fa-plus mr-2"></i>
                    Add Credits
                  </router-link>
                </div>
              </div>

              <!-- Resources -->
              <div class="bg-dark-800/70 backdrop-blur-md rounded-2xl p-8 border border-dark-700/80 hover:border-primary-500/30 transition-all duration-300 shadow-lg shadow-dark-950/20 hover:shadow-xl hover:shadow-primary-500/10">
                <div class="flex items-center gap-4 mb-6">
                  <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/20 transform hover:scale-105 transition-all duration-300">
                    <i class="fas fa-book text-xl text-white"></i>
                  </div>
                  <h2 class="text-xl font-bold text-white">Resources</h2>
                </div>
                
                <div class="space-y-4">
                  <a 
                    v-for="resource in resources" 
                    :key="resource.title"
                    :href="resource.url"
                    class="block p-4 bg-dark-900/50 hover:bg-dark-900/80 border border-dark-700/50 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:translate-y-[-2px] group"
                  >
                    <div class="flex items-center gap-3 mb-2">
                      <div class="w-8 h-8 rounded-lg bg-green-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
                        <i :class="[resource.icon, 'text-green-400']"></i>
                      </div>
                      <h3 class="text-white font-medium group-hover:text-green-400 transition-colors">{{ resource.title }}</h3>
                    </div>
                    <p class="text-gray-400 text-sm pl-11">{{ resource.description }}</p>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DashboardLayout } from '@/shared/layouts'
import { useAuthStore } from '@/apps/auth/store'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { CardContainer, StatCard } from '@/apps/home/components'
import { useNotification } from '@/shared/composables/useNotification'
import { ActionButton, IconButton, GradientText, ProgressBar } from '@/shared/components/atoms'
import {   
  EmptyState,
  ResourceLink
} from '@/shared/components/molecules'
import { ActivityFeed } from '@/shared/components/organisms'

// Store initialization
const authStore = useAuthStore()
const projectStore = useProjectStore()
const { showNotification } = useNotification()

// Reactive state
const credits = ref(1000)
const creditsUsed = ref(250)
const creditsPlan = ref(1000)
const activeBuildCount = ref(0)
const apiCallCount = ref(0)
const recentProjects = ref([])
const recentActivities = ref([])

// Stats data with computed values
const statsData = computed(() => [
  { 
    title: 'Total Projects', 
    value: projectStore.projects?.length || 0, 
    icon: 'fas fa-folder', 
    trend: '+12%', 
    color: 'primary' 
  },
  { 
    title: 'Active Builds', 
    value: activeBuildCount.value, 
    icon: 'fas fa-hammer', 
    trend: '+5%', 
    color: 'success' 
  },
  { 
    title: 'Credits Used', 
    value: creditsUsed.value, 
    icon: 'fas fa-coins', 
    trend: '-8%', 
    color: 'warning' 
  },
  { 
    title: 'API Calls', 
    value: apiCallCount.value, 
    icon: 'fas fa-bolt', 
    trend: '+25%', 
    color: 'info' 
  }
])

// Navigation configuration
const navigationItems = [
  { name: 'Dashboard', to: '/dashboard', icon: 'fas fa-home', exact: true },
  { name: 'Projects', to: '/products/oasis/builder/projects', icon: 'fas fa-folder' },
  { name: 'Credits', to: '/payments', icon: 'fas fa-coins' }
]

// Quick actions configuration
const quickActions = [
  { 
    title: 'New Project', 
    icon: 'fas fa-plus', 
    route: { name: 'products-builder-new-project' } 
  },
  { 
    title: 'Browse Templates', 
    icon: 'fas fa-box', 
    route: { name: 'products-builder-templates' } 
  },
  { 
    title: 'API Documentation', 
    icon: 'fas fa-book', 
    route: { name: 'docs-api' } 
  },
  { 
    title: 'Invite Team', 
    icon: 'fas fa-user-plus', 
    route: { name: 'settings-team' } 
  }
]

// Resources links
const resources = [
  { title: 'Documentation', icon: 'fas fa-book', url: '/docs', description: 'Learn how to use Imagi' },
  { title: 'API Reference', icon: 'fas fa-code', url: '/docs/api', description: 'Integrate with our API' },
  { title: 'Community', icon: 'fas fa-users', url: '/community', description: 'Join our Discord' }
]

// Format date helper
function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}

// Add navigation method
const router = useRouter()
const goToProject = (id) => {
  router.push({
    name: 'builder-workspace',
    params: { projectId: String(id) }
  }).catch(err => {
    console.error('Navigation error:', err)
    showNotification({
      type: 'error',
      message: 'Unable to load project details'
    })
  })
}

// Enhanced data fetching
async function fetchDashboardData() {
  try {
    if (projectStore.fetchProjects) {
      await projectStore.fetchProjects()
      recentProjects.value = projectStore.projects?.slice(0, 5) || []
    }
    
    // Fetch other data if methods exist, but don't fail if they error
    try {
      if (projectStore.fetchActivities) {
        recentActivities.value = await projectStore.fetchActivities()
      }
    } catch (err) {
      recentActivities.value = []
    }
    
    try {
      if (projectStore.fetchStats) {
        const stats = await projectStore.fetchStats()
        activeBuildCount.value = stats?.activeBuildCount || 0
        apiCallCount.value = stats?.apiCallCount || 0
        creditsUsed.value = stats?.creditsUsed || 0
      }
    } catch (err) {
      // Handle error silently
    }
  } catch (err) {
    showNotification({
      type: 'error',
      message: 'Failed to load dashboard data'
    })
  }
}

onMounted(() => {
  fetchDashboardData()
})
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

/* Slower pulsing animation for background elements */
@keyframes pulse-slow {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.2; }
}

.animate-pulse-slow {
  animation: pulse-slow 8s ease-in-out infinite;
}
</style>