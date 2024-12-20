import { ref, computed } from 'vue';
import axios from 'axios';

const projects = ref([]);
const currentProject = ref(null);
const loading = ref(false);
const error = ref(null);

export function useProjects() {
  /**
   * Fetch all projects for the current user
   */
  async function fetchProjects() {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get('/api/projects/');
      projects.value = response.data;
    } catch (err) {
      console.error('Failed to fetch projects:', err);
      error.value = err.response?.data?.message || 'Failed to fetch projects. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch a single project by ID
   * @param {string} projectId - The ID of the project to fetch
   */
  async function fetchProject(projectId) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get(`/api/projects/${projectId}/`);
      currentProject.value = response.data;
    } catch (err) {
      console.error('Failed to fetch project:', err);
      error.value = err.response?.data?.message || 'Failed to fetch project. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Create a new project
   * @param {Object} projectData - The project data
   * @param {string} projectData.name - Project name
   * @param {string} projectData.description - Project description
   * @param {string} projectData.template - Project template
   */
  async function createProject(projectData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/projects/', projectData);
      projects.value.push(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to create project:', err);
      error.value = err.response?.data?.message || 'Failed to create project. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Update an existing project
   * @param {string} projectId - The ID of the project to update
   * @param {Object} projectData - The updated project data
   */
  async function updateProject(projectId, projectData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.patch(`/api/projects/${projectId}/`, projectData);
      const index = projects.value.findIndex(p => p.id === projectId);
      if (index !== -1) {
        projects.value[index] = response.data;
      }
      if (currentProject.value?.id === projectId) {
        currentProject.value = response.data;
      }
      return response.data;
    } catch (err) {
      console.error('Failed to update project:', err);
      error.value = err.response?.data?.message || 'Failed to update project. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Delete a project
   * @param {string} projectId - The ID of the project to delete
   */
  async function deleteProject(projectId) {
    loading.value = true;
    error.value = null;

    try {
      await axios.delete(`/api/projects/${projectId}/`);
      projects.value = projects.value.filter(p => p.id !== projectId);
      if (currentProject.value?.id === projectId) {
        currentProject.value = null;
      }
    } catch (err) {
      console.error('Failed to delete project:', err);
      error.value = err.response?.data?.message || 'Failed to delete project. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Generate code for a project using AI
   * @param {string} projectId - The ID of the project
   * @param {Object} generationData - The generation parameters
   * @param {string} generationData.prompt - The natural language prompt
   * @param {string} generationData.context - Additional context for generation
   */
  async function generateProjectCode(projectId, generationData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post(`/api/projects/${projectId}/generate/`, generationData);
      return response.data;
    } catch (err) {
      console.error('Failed to generate code:', err);
      error.value = err.response?.data?.message || 'Failed to generate code. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Deploy a project
   * @param {string} projectId - The ID of the project to deploy
   * @param {Object} deploymentData - Deployment configuration
   */
  async function deployProject(projectId, deploymentData = {}) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post(`/api/projects/${projectId}/deploy/`, deploymentData);
      return response.data;
    } catch (err) {
      console.error('Failed to deploy project:', err);
      error.value = err.response?.data?.message || 'Failed to deploy project. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Computed properties
  const projectsList = computed(() => projects.value);
  const activeProject = computed(() => currentProject.value);
  const isLoading = computed(() => loading.value);
  const projectError = computed(() => error.value);

  return {
    // State
    projects: projectsList,
    currentProject: activeProject,
    isLoading,
    error: projectError,

    // Methods
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
    generateProjectCode,
    deployProject
  };
} 