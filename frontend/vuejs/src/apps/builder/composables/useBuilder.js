import { ref, computed } from 'vue';
import { useProjects } from './useProjects';
import { useAI } from './useAI';
import { BuilderAPI } from '../services/api';

// Define modes as constants
export const BUILDER_MODES = {
  CHAT: 'chat',
  BUILD: 'build'
};

// Define supported file types
export const FILE_TYPES = {
  HTML: 'html',
  CSS: 'css',
  JAVASCRIPT: 'javascript',
  PYTHON: 'python',
  MARKDOWN: 'markdown',
  TEXT: 'text'
};

const currentMode = ref(BUILDER_MODES.CHAT);
const selectedComponent = ref(null);
const componentTree = ref([]);
const loading = ref(false);
const error = ref(null);
const previewUrl = ref(null);
const editHistory = ref([]);
const currentHistoryIndex = ref(-1);

// Define available AI models
const DEFAULT_MODELS = [
  { id: 'gpt-4o', name: 'GPT-4o' },
  { id: 'gpt-4o-mini', name: 'GPT-4o Mini' },
  { id: 'claude-sonnet-3.5', name: 'Claude Sonnet 3.5' }
];

export function useBuilder() {
  const { currentProject } = useProjects();
  const { sendPrompt } = useAI();

  // State
  const files = ref([]);
  const selectedFile = ref(null);
  const fileContent = ref('');
  const availableModels = ref(DEFAULT_MODELS);
  const selectedModel = ref('gpt-4o');
  const isLoading = ref(false);
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
    loading.value = true;
    error.value = null;

    try {
      const response = await BuilderAPI.getComponentTree(projectId.value);
      componentTree.value = response.data;
    } catch (err) {
      console.error('Failed to load component tree:', err);
      error.value = err.response?.data?.message || 'Failed to load component tree';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Load project files
   */
  async function loadFiles() {
    if (!projectId.value) return;

    loading.value = true;
    error.value = null;

    try {
      const response = await BuilderAPI.getProjectFiles(projectId.value);
      files.value = response.data;
    } catch (err) {
      console.error('Failed to load project files:', err);
      error.value = err.response?.data?.message || 'Failed to load project files';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Select a file to edit
   */
  async function selectFile(file) {
    if (!file) return;

    loading.value = true;
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
      loading.value = false;
    }
  }

  /**
   * Update file content
   */
  async function updateFile(content) {
    if (!selectedFile.value) return;

    loading.value = true;
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
      loading.value = false;
    }
  }

  /**
   * Generate code using AI
   */
  async function generateCode(prompt) {
    loading.value = true;
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
      loading.value = false;
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

    loading.value = true;
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
      loading.value = false;
    }
  }

  /**
   * Load available AI models
   */
  async function loadAvailableModels() {
    try {
      const response = await BuilderAPI.getAvailableModels();
      // The response is already wrapped in { models: [...] } by the API service
      const supportedModels = response.models || [];
      
      // Use the filtered models if available, otherwise use defaults
      availableModels.value = supportedModels.length > 0 ? supportedModels : DEFAULT_MODELS;
    } catch (err) {
      console.error('Failed to load available models:', err);
      // Don't throw the error, just use defaults
      availableModels.value = DEFAULT_MODELS;
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
      
      const project = await BuilderAPI.getProject(id);
      if (!project) {
        throw new Error('Project not found');
      }
      
      currentProject.value = project;
      await loadFiles();
      await loadAvailableModels();
    } catch (err) {
      console.error('Error loading project:', err);
      error.value = err.response?.data?.message || 'Failed to load project';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  return {
    // State
    files,
    selectedFile,
    fileContent,
    availableModels,
    selectedModel,
    isLoading,
    error,
    hasUnsavedChanges,
    currentMode,
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