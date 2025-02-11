<template>
  <DefaultLayout>
    <div class="flex flex-col w-full pt-16">
      <!-- Header -->
      <header class="bg-white dark:bg-dark-900 shadow-sm border-b border-gray-200 dark:border-dark-700">
        <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <h1 class="text-4xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p class="mt-2 text-lg text-gray-600 dark:text-gray-400">Manage your projects and resources</p>
        </div>
      </header>

      <!-- Main Content -->
      <div class="py-8">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <!-- Stats Grid -->
          <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <!-- Projects Card -->
            <div class="bg-white dark:bg-dark-800 overflow-hidden rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 hover:border-primary-500 transition-all duration-300">
              <div class="p-6">
                <div class="flex items-center">
                  <div class="w-12 h-12 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center">
                    <svg class="h-6 w-6 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Total Projects</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-bold text-gray-900 dark:text-white">{{ projectCount }}</div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div class="bg-gray-50 dark:bg-dark-900 px-6 py-3">
                <div class="text-sm">
                  <router-link to="/builder/projects" class="font-medium text-primary-500 hover:text-primary-600 flex items-center">
                    View all projects
                    <svg class="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Credits Card -->
            <div class="bg-white dark:bg-dark-800 overflow-hidden rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 hover:border-primary-500 transition-all duration-300">
              <div class="p-6">
                <div class="flex items-center">
                  <div class="w-12 h-12 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center">
                    <svg class="h-6 w-6 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Available Credits</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-bold text-gray-900 dark:text-white">{{ credits }}</div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
              <div class="bg-gray-50 dark:bg-dark-900 px-6 py-3">
                <div class="text-sm">
                  <router-link to="/payments" class="font-medium text-primary-500 hover:text-primary-600 flex items-center">
                    Purchase credits
                    <svg class="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </router-link>
                </div>
              </div>
            </div>

            <!-- Recent Activity Card -->
            <div class="bg-white dark:bg-dark-800 overflow-hidden rounded-xl shadow-sm border border-gray-200 dark:border-dark-700 hover:border-primary-500 transition-all duration-300">
              <div class="p-6">
                <div class="flex items-center">
                  <div class="w-12 h-12 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center">
                    <svg class="h-6 w-6 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">Recent Activity</dt>
                      <dd class="mt-2">
                        <ul class="divide-y divide-gray-200 dark:divide-dark-700">
                          <li v-for="activity in recentActivities" :key="activity.id" class="py-3 text-sm text-gray-600 dark:text-gray-400">
                            {{ activity.description }}
                          </li>
                        </ul>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="mt-12">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Quick Actions</h2>
            <div class="grid grid-cols-1 gap-6 sm:grid-cols-3">
              <router-link 
                :to="{ name: 'builder-dashboard' }" 
                class="group relative rounded-xl border border-gray-200 dark:border-dark-700 bg-white dark:bg-dark-800 p-6 hover:border-primary-500 transition-all duration-300"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center group-hover:bg-opacity-20 transition-all duration-300">
                    <svg class="h-6 w-6 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">New Project</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Start building a new web application</p>
                  </div>
                </div>
              </router-link>

              <router-link 
                :to="{ name: 'builder-projects' }" 
                class="group relative rounded-xl border border-gray-200 dark:border-dark-700 bg-white dark:bg-dark-800 p-6 hover:border-primary-500 transition-all duration-300"
              >
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center group-hover:bg-opacity-20 transition-all duration-300">
                    <i class="fas fa-folder text-primary-500"></i>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">All Projects</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">View and manage your projects</p>
                  </div>
                </div>
              </router-link>

              <router-link to="/builder/templates" class="group relative rounded-xl border border-gray-200 dark:border-dark-700 bg-white dark:bg-dark-800 p-6 hover:border-primary-500 transition-all duration-300">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center group-hover:bg-opacity-20 transition-all duration-300">
                    <svg class="h-6 w-6 text-primary-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">Templates</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Browse pre-built templates</p>
                  </div>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { DefaultLayout } from '@/shared/layouts'
import { useAuthStore } from '@/apps/auth/store'
import { useProjectStore } from '@/apps/builder/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'

const authStore = useAuthStore()
const projectStore = useProjectStore()
const { showNotification } = useNotification()

const credits = ref(0)
const recentActivities = ref([])

// Use computed property instead of ref for projectCount
const projectCount = computed(() => projectStore.projects.length)

async function fetchData() {
  try {
    await projectStore.fetchProjects()
    // TODO: Fetch credits and activities from their respective stores
    credits.value = 0
    recentActivities.value = []
  } catch (err) {
    showNotification({
      type: 'error',
      message: 'Failed to fetch dashboard data'
    })
  }
}

onMounted(async () => {
  await fetchData()
})
</script>