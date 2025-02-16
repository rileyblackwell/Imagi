import { ref, computed } from 'vue';
import { useProjectStore } from '../stores/projectStore';

export function useProjects() {
  const projectStore = useProjectStore();

  return {
    projects: computed(() => projectStore.projects),
    currentProject: computed(() => projectStore.currentProject),
    loading: computed(() => projectStore.loading),
    error: computed(() => projectStore.error),
    fetchProjects: projectStore.fetchProjects,
    fetchProject: projectStore.fetchProject,
    createProject: projectStore.createProject,
    updateProject: projectStore.updateProject,
    deleteProject: projectStore.deleteProject,
    setCurrentProject: projectStore.setCurrentProject,
    clearError: projectStore.clearError
  };
} 