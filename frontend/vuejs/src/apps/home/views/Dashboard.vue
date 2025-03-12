<template>
  <DashboardLayout :navigationItems="navigationItems">
    <div class="flex flex-col w-full min-h-screen bg-dark-900">
      <!-- Enhanced Background -->
      <div class="absolute inset-0 bg-dark-900">
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-dark-900 to-violet-500/5"></div>
        <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/10 to-violet-500/10 rounded-full blur-[120px] opacity-50"></div>
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
      </div>

      <!-- Dashboard Content -->
      <div class="relative">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <!-- Welcome Section -->
          <div class="mb-12">
            <div class="mb-6">
              <GradientText variant="primary" size="3xl" class="font-bold">
                Main Dashboard
              </GradientText>
            </div>
            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-2xl font-bold text-white mb-2">
                  Welcome back, {{ authStore.user?.name || 'Developer' }}! 👋
                </h2>
                <p class="text-gray-400">
                  Here's what's happening with your projects today.
                </p>
              </div>
              <IconButton
                icon="fas fa-plus"
                variant="primary"
                size="lg"
                @click="$router.push({ name: 'builder-new-project' })"
              >
                New Project
              </IconButton>
            </div>
          </div>

          <!-- Stats Overview -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <StatsCard
              v-for="stat in statsData"
              :key="stat.title"
              v-bind="stat"
            />
          </div>

          <!-- Main Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Projects & Activity Column -->
            <div class="lg:col-span-2 space-y-8">
              <!-- Recent Projects -->
              <CardContainer title="Recent Projects" :showViewAll="true" viewAllLink="/products/oasis/builder/projects">
                <div class="space-y-4">
                  <ProjectListItem
                    v-for="project in recentProjects"
                    :key="project.id"
                    :project="project"
                    @click="goToProject(project.id)"
                  />
                  <EmptyState
                    v-if="!recentProjects.length"
                    icon="fas fa-folder-open"
                    title="No projects yet"
                    description="Start by creating your first project"
                  />
                </div>
              </CardContainer>

              <!-- Recent Activity -->
              <CardContainer title="Activity Feed" :showViewAll="true">
                <ActivityFeed :activities="recentActivities" />
              </CardContainer>
            </div>

            <!-- Quick Actions & Resources Column -->
            <div class="space-y-8">
              <!-- Quick Actions -->
              <CardContainer title="Quick Actions">
                <div class="space-y-3">
                  <ActionButton
                    v-for="action in quickActions"
                    :key="action.title"
                    v-bind="action"
                  />
                </div>
              </CardContainer>

              <!-- Available Credits -->
              <CardContainer title="Credits Overview">
                <div class="text-center p-4">
                  <div class="text-3xl font-bold text-primary-400 mb-2">
                    {{ credits }}
                  </div>
                  <p class="text-gray-400 mb-4">Available Credits</p>
                  <ProgressBar
                    :value="creditsUsed"
                    :total="creditsPlan"
                    class="mb-4"
                  />
                  <IconButton
                    to="/payments"
                    variant="outline"
                    size="sm"
                    icon="fas fa-plus"
                  >
                    Add Credits
                  </IconButton>
                </div>
              </CardContainer>

              <!-- Resources -->
              <CardContainer title="Resources">
                <div class="space-y-4">
                  <ResourceLink
                    v-for="resource in resources"
                    :key="resource.title"
                    v-bind="resource"
                  />
                </div>
              </CardContainer>
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
import { ProjectListItem, CardContainer, StatsCard } from '@/apps/home/components'
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
  { name: 'Templates', to: '/products/oasis/builder/templates', icon: 'fas fa-box' },
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