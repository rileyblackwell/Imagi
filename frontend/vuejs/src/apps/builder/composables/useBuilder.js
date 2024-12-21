import { ref, computed } from 'vue';
import axios from 'axios';
import { useProjects } from './useProjects';
import { useAI } from './useAI';

const currentMode = ref('chat'); // 'chat' or 'build'
const selectedComponent = ref(null);
const componentTree = ref([]);
const loading = ref(false);
const error = ref(null);
const previewUrl = ref(null);
const editHistory = ref([]);
const currentHistoryIndex = ref(-1);

export function useBuilder() {
  const { currentProject } = useProjects();
  const { sendPrompt } = useAI();

  /**
   * Switch between chat and build modes
   * @param {string} mode - The mode to switch to ('chat' or 'build')
   */
  function switchMode(mode) {
    if (mode !== 'chat' && mode !== 'build') {
      throw new Error('Invalid mode. Must be either "chat" or "build".');
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
      const response = await axios.get(`/api/builder/components/${currentProject.value?.id}/`);
      componentTree.value = response.data;
    } catch (err) {
      console.error('Failed to load component tree:', err);
      error.value = err.response?.data?.message || 'Failed to load component tree. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Select a component for editing
   * @param {Object} component - The component to select
   */
  function selectComponent(component) {
    selectedComponent.value = component;
  }

  /**
   * Update a component's properties
   * @param {string} componentId - The ID of the component to update
   * @param {Object} properties - The updated properties
   */
  async function updateComponent(componentId, properties) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.patch(`/api/builder/components/${componentId}/`, properties);
      
      // Update component in tree
      updateComponentInTree(componentId, response.data);
      
      // Add to edit history
      addToHistory({
        type: 'update',
        componentId,
        properties,
        timestamp: new Date().toISOString()
      });

      return response.data;
    } catch (err) {
      console.error('Failed to update component:', err);
      error.value = err.response?.data?.message || 'Failed to update component. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Add a new component to the tree
   * @param {Object} componentData - The component data
   * @param {string} parentId - The ID of the parent component
   */
  async function addComponent(componentData, parentId) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/builder/components/', {
        ...componentData,
        parent_id: parentId,
        project_id: currentProject.value?.id
      });

      // Add component to tree
      addComponentToTree(response.data, parentId);

      // Add to edit history
      addToHistory({
        type: 'add',
        component: response.data,
        parentId,
        timestamp: new Date().toISOString()
      });

      return response.data;
    } catch (err) {
      console.error('Failed to add component:', err);
      error.value = err.response?.data?.message || 'Failed to add component. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Remove a component from the tree
   * @param {string} componentId - The ID of the component to remove
   */
  async function removeComponent(componentId) {
    loading.value = true;
    error.value = null;

    try {
      await axios.delete(`/api/builder/components/${componentId}/`);
      
      // Store component data before removal for history
      const removedComponent = findComponentInTree(componentId);
      
      // Remove from tree
      removeComponentFromTree(componentId);

      // Add to edit history
      addToHistory({
        type: 'remove',
        component: removedComponent,
        timestamp: new Date().toISOString()
      });

      if (selectedComponent.value?.id === componentId) {
        selectedComponent.value = null;
      }
    } catch (err) {
      console.error('Failed to remove component:', err);
      error.value = err.response?.data?.message || 'Failed to remove component. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Move a component in the tree
   * @param {string} componentId - The ID of the component to move
   * @param {string} newParentId - The ID of the new parent component
   * @param {number} position - The position in the new parent's children
   */
  async function moveComponent(componentId, newParentId, position) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post(`/api/builder/components/${componentId}/move/`, {
        new_parent_id: newParentId,
        position
      });

      // Update tree structure
      moveComponentInTree(componentId, newParentId, position);

      // Add to edit history
      addToHistory({
        type: 'move',
        componentId,
        newParentId,
        position,
        timestamp: new Date().toISOString()
      });

      return response.data;
    } catch (err) {
      console.error('Failed to move component:', err);
      error.value = err.response?.data?.message || 'Failed to move component. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Generate preview URL for the current state
   */
  async function generatePreview() {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post(`/api/builder/preview/${currentProject.value?.id}/`);
      previewUrl.value = response.data.url;
      return response.data.url;
    } catch (err) {
      console.error('Failed to generate preview:', err);
      error.value = err.response?.data?.message || 'Failed to generate preview. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Add an action to the edit history
   * @param {Object} action - The action to add to history
   */
  function addToHistory(action) {
    // Remove any future history if we're not at the latest point
    if (currentHistoryIndex.value < editHistory.value.length - 1) {
      editHistory.value = editHistory.value.slice(0, currentHistoryIndex.value + 1);
    }

    editHistory.value.push(action);
    currentHistoryIndex.value = editHistory.value.length - 1;
  }

  /**
   * Undo the last action
   */
  async function undo() {
    if (currentHistoryIndex.value < 0) return;

    const action = editHistory.value[currentHistoryIndex.value];
    try {
      switch (action.type) {
        case 'update':
          await updateComponent(action.componentId, action.previousProperties);
          break;
        case 'add':
          await removeComponent(action.component.id);
          break;
        case 'remove':
          await addComponent(action.component, action.component.parent_id);
          break;
        case 'move':
          await moveComponent(action.componentId, action.previousParentId, action.previousPosition);
          break;
      }
      currentHistoryIndex.value--;
    } catch (err) {
      console.error('Failed to undo action:', err);
      error.value = 'Failed to undo action. Please try again.';
    }
  }

  /**
   * Redo the last undone action
   */
  async function redo() {
    if (currentHistoryIndex.value >= editHistory.value.length - 1) return;

    const action = editHistory.value[currentHistoryIndex.value + 1];
    try {
      switch (action.type) {
        case 'update':
          await updateComponent(action.componentId, action.properties);
          break;
        case 'add':
          await addComponent(action.component, action.parentId);
          break;
        case 'remove':
          await removeComponent(action.component.id);
          break;
        case 'move':
          await moveComponent(action.componentId, action.newParentId, action.position);
          break;
      }
      currentHistoryIndex.value++;
    } catch (err) {
      console.error('Failed to redo action:', err);
      error.value = 'Failed to redo action. Please try again.';
    }
  }

  // Helper functions for tree manipulation
  function updateComponentInTree(componentId, updatedData) {
    function update(components) {
      return components.map(component => {
        if (component.id === componentId) {
          return { ...component, ...updatedData };
        }
        if (component.children) {
          return {
            ...component,
            children: update(component.children)
          };
        }
        return component;
      });
    }
    componentTree.value = update(componentTree.value);
  }

  function addComponentToTree(component, parentId) {
    function add(components) {
      return components.map(c => {
        if (c.id === parentId) {
          return {
            ...c,
            children: [...(c.children || []), component]
          };
        }
        if (c.children) {
          return {
            ...c,
            children: add(c.children)
          };
        }
        return c;
      });
    }
    componentTree.value = add(componentTree.value);
  }

  function removeComponentFromTree(componentId) {
    function remove(components) {
      return components.filter(c => {
        if (c.id === componentId) return false;
        if (c.children) {
          c.children = remove(c.children);
        }
        return true;
      });
    }
    componentTree.value = remove(componentTree.value);
  }

  function moveComponentInTree(componentId, newParentId, position) {
    let componentToMove;

    // First, find and remove the component
    function findAndRemove(components) {
      return components.filter(c => {
        if (c.id === componentId) {
          componentToMove = c;
          return false;
        }
        if (c.children) {
          c.children = findAndRemove(c.children);
        }
        return true;
      });
    }

    // Then, add it to its new position
    function addToNewPosition(components) {
      return components.map(c => {
        if (c.id === newParentId) {
          const newChildren = [...(c.children || [])];
          newChildren.splice(position, 0, componentToMove);
          return { ...c, children: newChildren };
        }
        if (c.children) {
          return { ...c, children: addToNewPosition(c.children) };
        }
        return c;
      });
    }

    componentTree.value = findAndRemove(componentTree.value);
    componentTree.value = addToNewPosition(componentTree.value);
  }

  function findComponentInTree(componentId) {
    function find(components) {
      for (const component of components) {
        if (component.id === componentId) return component;
        if (component.children) {
          const found = find(component.children);
          if (found) return found;
        }
      }
      return null;
    }
    return find(componentTree.value);
  }

  // Computed properties
  const mode = computed(() => currentMode.value);
  const selectedComponentData = computed(() => selectedComponent.value);
  const tree = computed(() => componentTree.value);
  const isLoading = computed(() => loading.value);
  const builderError = computed(() => error.value);
  const canUndo = computed(() => currentHistoryIndex.value >= 0);
  const canRedo = computed(() => currentHistoryIndex.value < editHistory.value.length - 1);

  return {
    // State
    mode,
    selectedComponent: selectedComponentData,
    componentTree: tree,
    isLoading,
    error: builderError,
    previewUrl,
    canUndo,
    canRedo,

    // Methods
    switchMode,
    loadComponentTree,
    selectComponent,
    updateComponent,
    addComponent,
    removeComponent,
    moveComponent,
    generatePreview,
    undo,
    redo
  };
} 