<template>
  <BuilderLayout storage-key="builderDashboardSidebarCollapsed">
    <div class="min-h-full bg-dark-950 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Header Section -->
        <div class="mb-12">
          <div class="flex flex-col items-center text-center space-y-4">
            <div class="p-3 bg-primary-500/10 rounded-2xl">
              <i class="fas fa-wand-magic-sparkles text-2xl text-primary-400"></i>
            </div>
            <h1 class="text-4xl font-bold text-white">Welcome to Imagi Builder</h1>
            <p class="text-xl text-gray-400 max-w-2xl">
              Create and manage your web projects using AI-powered tools.
            </p>
          </div>
        </div>

        <!-- Cards Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <NewProjectCard
            v-model="newProjectName"
            :is-loading="isCreating"
            @submit="createProject"
          />
          
          <ProjectList
            :projects="projects"
            :is-loading="isLoading"
            :error="error"
            @delete="confirmDelete"
            @retry="retryFetch"
          />
        </div>
      </div>
    </div>
  </BuilderLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { BuilderLayout } from '../layouts';
import { useProjectStore } from '../stores/projectStore';
import { NewProjectCard, ProjectList } from '../components';
import { useNotification } from '@/shared/composables/useNotification';

const router = useRouter();
const projectStore = useProjectStore();
const { showNotification } = useNotification();

// State
const newProjectName = ref('');
const isCreating = ref(false);

// Computed
const projects = computed(() => projectStore.sortedProjects);
const isLoading = computed(() => projectStore.loading);
const error = computed(() => projectStore.error);

// Navigation items
const navigationItems = [
  { 
    name: 'Projects', 
    to: '/builder/dashboard', 
    icon: 'fas fa-folder',
    exact: true
  },
  { 
    name: 'Settings', 
    to: '/builder/settings', 
    icon: 'fas fa-cog'
  }
];

// Methods
async function createProject() {
  if (!newProjectName.value.trim() || isCreating.value) return;

  isCreating.value = true;
  try {
    const project = await projectStore.createProject({
      name: newProjectName.value.trim(),
      description: ''
    });
    
    if (!project?.id && project?.id !== 0) {
      throw new Error('Failed to create project - no ID returned');
    }

    showNotification({
      type: 'success',
      message: 'Project created successfully!'
    });

    // Clear input and navigate to the new project
    newProjectName.value = '';
    
    // Ensure we have a valid project ID before navigation
    const projectId = String(project.id);
    if (!projectId) {
      throw new Error('Invalid project ID for navigation');
    }

    await router.push({
      name: 'builder-workspace',
      params: { projectId }
    });
  } catch (err) {
    console.error('Project creation error:', err);
    showNotification({
      type: 'error',
      message: err.message || 'Failed to create project'
    });
  } finally {
    isCreating.value = false;
  }
}

async function confirmDelete(project) {
  if (!confirm(`Are you sure you want to delete "${project.name}"?`)) {
    return;
  }

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

// Lifecycle
onMounted(fetchProjects);
</script>

<style scoped>
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