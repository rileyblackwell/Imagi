import { ref, computed } from 'vue';
import { useProjectStore } from '../stores/projectStore';
import { useAI } from './useAI';
import { BUILDER_MODES, FILE_TYPES } from '../utils/constants';
import { BuilderAPI } from '../services/api';

export function useBuilder() {
  const store = useProjectStore();
  const { sendPrompt, generating: aiGenerating } = useAI();
  
  // Local state
  const currentProject = ref(null);
  const isLoading = ref(false);
  const currentMode = ref(BUILDER_MODES.CHAT);
  const error = ref(null);
  const componentTree = ref([]);
  const selectedComponent = ref(null);

  // State
  const files = ref([]);
  const selectedFile = ref(null);
  const fileContent = ref('');
  const hasUnsavedChanges = ref(false);

  // Computed
  const projectId = computed(() => currentProject.value?.id);

  /**
   * Switch between chat and build modes
   * @param {string} mode - The mode to switch to ('chat' or 'build')
   */
  function switchMode(mode) {
    if (!Object.values(BUILDER_MODES).includes(mode)) {
      throw new Error(`Invalid mode. Must be one of: ${Object.values(BUILDER_MODES).join(', ')}`);
    }
    currentMode.value = mode;
  }

  /**
   * Load the component tree for the current project
   */
  async function loadComponentTree() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await BuilderAPI.getComponentTree(projectId.value);
      componentTree.value = response.data;
    } catch (err) {
      console.error('Failed to load component tree:', err);
      error.value = err.response?.data?.message || 'Failed to load component tree';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load project files
   */
  async function loadFiles() {
    if (!projectId.value) return;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await BuilderAPI.getProjectFiles(projectId.value);
      files.value = response.data;
    } catch (err) {
      console.error('Failed to load project files:', err);
      error.value = err.response?.data?.message || 'Failed to load project files';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Select a file to edit
   */
  async function selectFile(file) {
    if (!file) return;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await BuilderAPI.getFileContent(projectId.value, file.path);
      selectedFile.value = file;
      fileContent.value = response.data.content;
    } catch (err) {
      console.error('Failed to load file content:', err);
      error.value = err.response?.data?.message || 'Failed to load file content';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update file content
   */
  async function updateFile(content) {
    if (!selectedFile.value) return;

    isLoading.value = true;
    error.value = null;

    try {
      await BuilderAPI.updateFileContent(projectId.value, selectedFile.value.path, content);
      fileContent.value = content;
      hasUnsavedChanges.value = false;
    } catch (err) {
      console.error('Failed to update file:', err);
      error.value = err.response?.data?.message || 'Failed to update file';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Generate code using AI
   */
  async function generateCode(prompt) {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await BuilderAPI.generateCode(projectId.value, {
        prompt,
        mode: currentMode.value,
        model: selectedModel.value,
        file: selectedFile.value?.path
      });
      return response.data.code;
    } catch (err) {
      console.error('Failed to generate code:', err);
      error.value = err.response?.data?.message || 'Failed to generate code';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Undo last action
   */
  async function undoLastAction() {
    if (currentHistoryIndex.value < 0) return;

    try {
      const lastAction = editHistory.value[currentHistoryIndex.value];
      await BuilderAPI.undoAction(projectId.value, lastAction.id);
      currentHistoryIndex.value--;
      await loadFiles();
    } catch (err) {
      console.error('Failed to undo action:', err);
      error.value = err.response?.data?.message || 'Failed to undo action';
      throw err;
    }
  }

  /**
   * Create a new file
   */
  async function createFile(fileName, fileType, initialContent = '') {
    if (!projectId.value || !fileName || !fileType) return;

    isLoading.value = true;
    error.value = null;

    try {
      const response = await BuilderAPI.createFile(projectId.value, {
        name: fileName,
        type: fileType,
        content: initialContent
      });
      
      // Refresh the file list
      await loadFiles();
      
      // Select the newly created file
      const newFile = files.value.find(f => f.path === response.data.path);
      if (newFile) {
        await selectFile(newFile);
      }
      
      return response.data;
    } catch (err) {
      console.error('Failed to create file:', err);
      error.value = err.response?.data?.message || 'Failed to create file';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load available AI models
   */
  async function loadAvailableModels() {
    try {
      await store.fetchAvailableModels();
    } catch (err) {
      console.error('Failed to load available models:', err);
      error.value = 'Failed to load AI models';
    }
  }

  // Methods
  const loadProject = async (id) => {
    if (!id) {
      console.error('Project ID is required');
      error.value = 'Invalid project ID';
      return;
    }

    try {
      isLoading.value = true;
      error.value = null;
      
      const project = await store.fetchProject(id);
      if (!project) {
        throw new Error('Project not found');
      }
      
      currentProject.value = project;
      await loadFiles();
      await loadAvailableModels();
    } catch (err) {
      console.error('Error loading project:', err);
      error.value = err.message || 'Failed to load project';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    // State
    currentProject,
    availableModels: computed(() => store.availableModels),
    selectedModel: computed({
      get: () => store.selectedModel,
      set: (value) => store.setSelectedModel(value)
    }),
    isLoading: computed(() => isLoading.value || store.loading),
    error: computed(() => error.value || store.error),
    files,
    selectedFile,
    fileContent,
    hasUnsavedChanges,
    currentMode,
    aiGenerating,
    componentTree,
    selectedComponent,
    FILE_TYPES,

    // Methods
    loadFiles,
    selectFile,
    updateFile,
    createFile,
    generateCode,
    undoLastAction,
    loadAvailableModels,
    loadComponentTree,
    switchMode,
    loadProject
  };
}