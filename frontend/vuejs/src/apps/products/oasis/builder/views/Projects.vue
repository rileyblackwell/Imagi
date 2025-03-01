<template>
  <BuilderLayout 
    storage-key="projectsViewSidebarCollapsed"
    :navigation-items="navigationItems"
  >
    <div class="min-h-screen bg-dark-900">
      <!-- Header -->
      <div class="bg-dark-800 border-b border-dark-700 py-8 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <div class="md:flex md:items-center md:justify-between">
            <div class="flex-1 min-w-0">
              <h1 class="text-3xl font-bold text-white">Projects</h1>
              <p class="mt-2 text-lg text-gray-400">
                Manage and organize all your web applications
              </p>
            </div>
            <div class="mt-4 flex md:mt-0 md:ml-4">
              <button
                @click="$router.push({ name: 'builder-dashboard' })"
                class="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-500 hover:bg-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <i class="fas fa-plus mr-2"></i>
                New Project
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Project List -->
      <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div v-if="isLoading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary-500"></div>
          <p class="mt-2 text-sm text-gray-400">Loading projects...</p>
        </div>

        <div v-else-if="error" class="text-center py-12">
          <div class="text-red-500 mb-4">
            <i class="fas fa-exclamation-circle text-xl"></i>
          </div>
          <p class="text-gray-400">{{ error }}</p>
          <button
            @click="retryFetch"
            class="mt-4 text-primary-500 hover:text-primary-400"
          >
            Try again
          </button>
        </div>

        <div v-else-if="projects.length === 0" class="text-center py-12">
          <div class="text-gray-400 mb-4">
            <i class="fas fa-folder-open text-xl"></i>
          </div>
          <p class="text-gray-400">No projects yet</p>
          <button
            @click="$router.push({ name: 'builder-dashboard' })"
            class="mt-4 text-primary-500 hover:text-primary-400"
          >
            Create your first project
          </button>
        </div>

        <div v-else class="grid gap-6">
          <div
            v-for="project in sortedProjects"
            :key="project.id"
            class="bg-dark-800 border border-dark-700 rounded-lg shadow-sm hover:border-primary-500 transition-colors duration-200"
          >
            <div class="p-6">
              <div class="flex items-center justify-between">
                <div>
                  <h3 class="text-lg font-medium text-white">
                    {{ project.name }}
                  </h3>
                  <p class="mt-1 text-sm text-gray-400">
                    {{ project.description || 'No description' }}
                  </p>
                </div>
                <div class="flex items-center space-x-4">
                  <button
                    @click="$router.push({ name: 'builder-workspace', params: { projectId: project.id }})"
                    class="text-gray-400 hover:text-white"
                    title="Open project"
                  >
                    <i class="fas fa-arrow-right"></i>
                  </button>
                  <button
                    @click="confirmDelete(project)"
                    class="text-gray-400 hover:text-red-500"
                    title="Delete project"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
              <div class="mt-4 flex items-center text-sm text-gray-500">
                <i class="fas fa-clock mr-2"></i>
                Last updated {{ new Date(project.updated_at).toLocaleDateString() }}
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

const router = useRouter();
const projectStore = useProjectStore();
const { showNotification } = useNotification();

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

async function confirmDelete(project) {
  if (!confirm(`Are you sure you want to delete "${project.name}"?`)) return;

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

onMounted(fetchProjects);
</script>
