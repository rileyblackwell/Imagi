<template>
  <DashboardLayout :navigationItems="navigationItems">
    <div class="flex flex-col w-full min-h-screen bg-dark-950 relative overflow-hidden">
      <!-- Enhanced Background Effects matching Projects page -->
      <div class="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <!-- Gradient orbs matching Projects page -->
        <div class="absolute top-[10%] left-[5%] w-[300px] sm:w-[500px] md:w-[800px] h-[300px] sm:h-[500px] md:h-[800px] rounded-full bg-primary-500/5 blur-[80px] sm:blur-[120px] animate-float"></div>
        <div class="absolute bottom-[20%] right-[10%] w-[200px] sm:w-[400px] md:w-[600px] h-[200px] sm:h-[400px] md:h-[600px] rounded-full bg-violet-500/5 blur-[60px] sm:blur-[100px] animate-float-delay"></div>
        <!-- Grid pattern overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <!-- Subtle noise texture -->
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
      </div>

      <!-- Dashboard Content with improved spacing and organization -->
      <div class="relative z-10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
          <!-- Welcome Section with Enhanced Imagi Title Styling -->
          <div class="mb-12">
            <!-- Enhanced section header to match projects page -->
            <div class="inline-block px-4 py-1.5 bg-primary-500/10 rounded-full mb-4">
              <span class="text-primary-400 font-semibold text-sm tracking-wider">YOUR DASHBOARD</span>
            </div>
            
            <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <h2 class="text-4xl md:text-5xl font-bold text-white mb-4 leading-tight">
                  Welcome back, {{ authStore.user?.name || 'Developer' }}! 👋
                </h2>
                <p class="text-xl text-gray-300 max-w-3xl leading-relaxed">
                  Here's what's happening with your projects today.
                </p>
              </div>
              <button
                @click="$router.push({ name: 'builder-new-project' })"
                class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 text-white rounded-xl hover:from-primary-600 hover:to-violet-600 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:-translate-y-1 transition-all duration-300 self-start"
              >
                <i class="fas fa-plus mr-2.5"></i>
                New Project
              </button>
            </div>
          </div>

          <!-- Divider with animated line matching Projects page -->
          <div class="relative h-16 max-w-7xl mx-auto mb-8">
            <div class="absolute inset-x-0 h-px mx-auto w-2/3 sm:w-1/2 bg-gradient-to-r from-transparent via-primary-500/30 to-transparent animate-pulse-slow"></div>
          </div>

          <!-- Stats Overview with Enhanced Cards and Consistent Styling -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-12">
            <div 
              v-for="stat in statsData" 
              :key="stat.title"
              class="group relative transform transition-all duration-300 hover:-translate-y-2"
            >
              <!-- Enhanced glass morphism effect with glow -->
              <div class="absolute -inset-0.5 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"
                :class="{
                  'bg-gradient-to-r from-primary-500/50 to-violet-500/50': stat.color === 'primary',
                  'bg-gradient-to-r from-green-500/50 to-emerald-500/50': stat.color === 'success',
                  'bg-gradient-to-r from-yellow-500/50 to-amber-500/50': stat.color === 'warning',
                  'bg-gradient-to-r from-blue-500/50 to-sky-500/50': stat.color === 'info'
                }"
              ></div>
              
              <!-- Card content with enhanced styling -->
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden h-full flex flex-col border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                <!-- Card header with gradient matching project color -->
                <div class="h-2 w-full"
                  :class="{
                    'bg-gradient-to-r from-primary-500 to-violet-500': stat.color === 'primary',
                    'bg-gradient-to-r from-green-500 to-emerald-500': stat.color === 'success',
                    'bg-gradient-to-r from-yellow-500 to-amber-500': stat.color === 'warning',
                    'bg-gradient-to-r from-blue-500 to-sky-500': stat.color === 'info'
                  }"
                ></div>
                
                <div class="p-5">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-medium text-gray-300">{{ stat.title }}</h3>
                    <div class="w-10 h-10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-all duration-300"
                      :class="{
                        'bg-primary-500/15 text-primary-400': stat.color === 'primary',
                        'bg-green-500/15 text-green-400': stat.color === 'success',
                        'bg-yellow-500/15 text-yellow-400': stat.color === 'warning',
                        'bg-blue-500/15 text-blue-400': stat.color === 'info'
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
          </div>

          <!-- Main Grid with Enhanced Cards -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Projects & Activity Column -->
            <div class="lg:col-span-2 space-y-8">
              <!-- Recent Projects -->
              <div class="group relative">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-primary-500 to-violet-500"></div>
                  <div class="p-8">
                    <div class="flex items-center justify-between mb-6">
                      <div class="flex items-center gap-4">
                        <div class="w-12 h-12 bg-gradient-to-br from-primary-500/20 to-violet-500/20 rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/10 transform hover:scale-105 transition-all duration-300 border border-primary-500/20">
                          <i class="fas fa-folder-open text-xl text-primary-400"></i>
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
                        class="group bg-dark-800/50 hover:bg-dark-800/80 border border-dark-700/50 hover:border-primary-500/30 rounded-xl p-4 transition-all duration-300 transform hover:-translate-y-1 cursor-pointer"
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
                      
                      <div v-if="!recentProjects.length" class="flex flex-col items-center justify-center py-10 bg-dark-800/30 rounded-xl border border-dark-700/50">
                        <div class="w-16 h-16 bg-primary-500/10 rounded-full flex items-center justify-center mb-5">
                          <i class="fas fa-folder-open text-2xl text-primary-400"></i>
                        </div>
                        <h3 class="text-xl font-semibold text-white mb-2">No projects yet</h3>
                        <p class="text-gray-300 text-center max-w-md mb-6">Create your first project to start building with Imagi</p>
                        <button
                          @click="$router.push({ name: 'builder-new-project' })"
                          class="px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 hover:from-primary-600 hover:to-violet-600 text-white rounded-xl shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:-translate-y-1 transition-all duration-300"
                        >
                          <i class="fas fa-plus mr-2"></i>
                          Create Your First Project
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Recent Activity -->
              <div class="group relative">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-violet-500"></div>
                  <div class="p-8">
                    <div class="flex items-center gap-4 mb-6">
                      <div class="w-12 h-12 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/10 transform hover:scale-105 transition-all duration-300 border border-indigo-500/20">
                        <i class="fas fa-history text-xl text-indigo-400"></i>
                      </div>
                      <h2 class="text-xl font-bold text-white">Activity Feed</h2>
                    </div>
                    
                    <ActivityFeed :activities="recentActivities" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions & Resources Column -->
            <div class="space-y-8">
              <!-- Quick Actions -->
              <div class="group relative">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-blue-500/50 to-cyan-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-blue-500 to-cyan-500"></div>
                  <div class="p-8">
                    <div class="flex items-center gap-4 mb-6">
                      <div class="w-12 h-12 bg-gradient-to-br from-blue-500/20 to-cyan-500/20 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/10 transform hover:scale-105 transition-all duration-300 border border-blue-500/20">
                        <i class="fas fa-bolt text-xl text-blue-400"></i>
                      </div>
                      <h2 class="text-xl font-bold text-white">Quick Actions</h2>
                    </div>
                    
                    <div class="space-y-3">
                      <button
                        v-for="action in quickActions"
                        :key="action.title"
                        @click="$router.push(action.route)"
                        class="w-full flex items-center justify-between p-4 bg-dark-800/50 hover:bg-dark-800/80 border border-dark-700/50 hover:border-primary-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 text-white hover:text-primary-400 group"
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
                </div>
              </div>

              <!-- Resources -->
              <div class="group relative">
                <!-- Enhanced glass morphism effect with glow -->
                <div class="absolute -inset-0.5 bg-gradient-to-r from-emerald-500/50 to-teal-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
                
                <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-xl overflow-hidden border border-dark-800/50 group-hover:border-primary-500/30 transition-all duration-300">
                  <!-- Card header with gradient -->
                  <div class="h-2 w-full bg-gradient-to-r from-emerald-500 to-teal-500"></div>
                  <div class="p-8">
                    <div class="flex items-center gap-4 mb-6">
                      <div class="w-12 h-12 bg-gradient-to-br from-emerald-500/20 to-teal-500/20 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/10 transform hover:scale-105 transition-all duration-300 border border-emerald-500/20">
                        <i class="fas fa-book text-xl text-emerald-400"></i>
                      </div>
                      <h2 class="text-xl font-bold text-white">Resources</h2>
                    </div>
                    
                    <div class="space-y-3">
                      <a 
                        v-for="resource in resourceLinks" 
                        :key="resource.title"
                        :href="resource.url"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="block p-4 bg-dark-800/50 hover:bg-dark-800/80 border border-dark-700/50 hover:border-emerald-500/30 rounded-xl transition-all duration-300 transform hover:-translate-y-1 group"
                      >
                        <div class="flex items-center justify-between">
                          <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
                              <i :class="[resource.icon, 'text-emerald-400']"></i>
                            </div>
                            <div>
                              <h3 class="text-white group-hover:text-emerald-400 transition-colors font-medium">{{ resource.title }}</h3>
                              <p class="text-sm text-gray-400">{{ resource.description }}</p>
                            </div>
                          </div>
                          <i class="fas fa-external-link-alt text-gray-500 group-hover:text-emerald-400 transition-colors"></i>
                        </div>
                      </a>
                    </div>
                  </div>
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
</style>