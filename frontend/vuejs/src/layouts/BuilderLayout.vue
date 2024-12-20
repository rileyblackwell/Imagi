<template>
  <div class="builder-layout">
    <!-- Builder header -->
    <header class="builder-header">
      <div class="header-left">
        <router-link to="/projects" class="btn btn-icon" title="Back to Projects">
          <i class="fas fa-arrow-left"></i>
        </router-link>
        <h1 class="project-title">{{ currentProject?.name || 'Untitled Project' }}</h1>
        <span class="project-status" :class="currentProject?.status">
          {{ currentProject?.status }}
        </span>
      </div>

      <div class="header-center">
        <div class="mode-switcher">
          <button
            class="mode-button"
            :class="{ active: mode === 'chat' }"
            @click="switchMode('chat')"
          >
            <i class="fas fa-comments"></i>
            Chat Mode
          </button>
          <button
            class="mode-button"
            :class="{ active: mode === 'build' }"
            @click="switchMode('build')"
          >
            <i class="fas fa-magic"></i>
            Build Mode
          </button>
        </div>
      </div>

      <div class="header-right">
        <button
          class="btn btn-outline btn-sm"
          @click="generatePreview"
          :disabled="isGenerating"
        >
          <i class="fas fa-eye"></i>
          Preview
        </button>
        <button
          class="btn btn-primary btn-sm"
          @click="deployProject"
          :disabled="isGenerating"
        >
          <i class="fas fa-rocket"></i>
          Deploy
        </button>
      </div>
    </header>

    <!-- Builder content -->
    <div class="builder-content">
      <!-- Component tree sidebar -->
      <aside class="component-sidebar" :class="{ 'sidebar-collapsed': isSidebarCollapsed }">
        <div class="sidebar-header">
          <h2 class="sidebar-title">Components</h2>
          <button class="btn btn-icon" @click="toggleSidebar">
            <i class="fas" :class="isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
          </button>
        </div>

        <div class="component-tree">
          <template v-if="componentTree.length">
            <div
              v-for="component in componentTree"
              :key="component.id"
              class="component-item"
              :class="{ active: selectedComponent?.id === component.id }"
              @click="selectComponent(component)"
            >
              <i class="component-icon" :class="getComponentIcon(component.type)"></i>
              <span class="component-name">{{ component.name }}</span>
            </div>
          </template>
          <div v-else class="empty-state">
            <i class="fas fa-cube"></i>
            <p>No components yet</p>
            <button class="btn btn-primary btn-sm" @click="addComponent">
              Add Component
            </button>
          </div>
        </div>

        <div class="sidebar-footer">
          <button
            class="btn btn-outline btn-sm undo-button"
            @click="undo"
            :disabled="!canUndo"
          >
            <i class="fas fa-undo"></i>
            Undo
          </button>
          <button
            class="btn btn-outline btn-sm redo-button"
            @click="redo"
            :disabled="!canRedo"
          >
            <i class="fas fa-redo"></i>
            Redo
          </button>
        </div>
      </aside>

      <!-- Main workspace -->
      <main class="workspace">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- Properties panel -->
      <aside class="properties-panel" v-if="selectedComponent && mode === 'build'">
        <div class="panel-header">
          <h2 class="panel-title">Properties</h2>
          <button class="btn btn-icon" @click="closeProperties">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="panel-content">
          <div class="property-group">
            <label class="property-label">Name</label>
            <input
              type="text"
              class="form-input"
              v-model="selectedComponent.name"
              @change="updateComponent"
            />
          </div>

          <div class="property-group">
            <label class="property-label">Type</label>
            <select
              class="form-input"
              v-model="selectedComponent.type"
              @change="updateComponent"
            >
              <option value="container">Container</option>
              <option value="text">Text</option>
              <option value="image">Image</option>
              <option value="button">Button</option>
              <option value="form">Form</option>
            </select>
          </div>

          <!-- Dynamic properties based on component type -->
          <template v-if="selectedComponent.type === 'text'">
            <div class="property-group">
              <label class="property-label">Content</label>
              <textarea
                class="form-input"
                v-model="selectedComponent.content"
                @change="updateComponent"
              ></textarea>
            </div>
          </template>

          <template v-if="selectedComponent.type === 'image'">
            <div class="property-group">
              <label class="property-label">Source URL</label>
              <input
                type="text"
                class="form-input"
                v-model="selectedComponent.src"
                @change="updateComponent"
              />
            </div>
            <div class="property-group">
              <label class="property-label">Alt Text</label>
              <input
                type="text"
                class="form-input"
                v-model="selectedComponent.alt"
                @change="updateComponent"
              />
            </div>
          </template>

          <template v-if="selectedComponent.type === 'button'">
            <div class="property-group">
              <label class="property-label">Text</label>
              <input
                type="text"
                class="form-input"
                v-model="selectedComponent.text"
                @change="updateComponent"
              />
            </div>
            <div class="property-group">
              <label class="property-label">Variant</label>
              <select
                class="form-input"
                v-model="selectedComponent.variant"
                @change="updateComponent"
              >
                <option value="primary">Primary</option>
                <option value="secondary">Secondary</option>
                <option value="outline">Outline</option>
              </select>
            </div>
          </template>
        </div>

        <div class="panel-footer">
          <button
            class="btn btn-error btn-sm"
            @click="removeComponent(selectedComponent.id)"
          >
            <i class="fas fa-trash"></i>
            Delete Component
          </button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useBuilder } from '@/composables/useBuilder';
import { useProjects } from '@/composables/useProjects';

// Router
const router = useRouter();

// Composables
const {
  mode,
  selectedComponent,
  componentTree,
  isLoading: isGenerating,
  canUndo,
  canRedo,
  switchMode,
  loadComponentTree,
  selectComponent,
  updateComponent,
  removeComponent,
  generatePreview,
  undo,
  redo
} = useBuilder();

const { currentProject, deployProject } = useProjects();

// State
const isSidebarCollapsed = ref(false);

// Methods
function toggleSidebar() {
  isSidebarCollapsed.value = !isSidebarCollapsed.value;
  localStorage.setItem('builderSidebarCollapsed', isSidebarCollapsed.value);
}

function closeProperties() {
  selectComponent(null);
}

function getComponentIcon(type) {
  switch (type) {
    case 'container':
      return 'fas fa-square-full';
    case 'text':
      return 'fas fa-font';
    case 'image':
      return 'fas fa-image';
    case 'button':
      return 'fas fa-square';
    case 'form':
      return 'fas fa-wpforms';
    default:
      return 'fas fa-cube';
  }
}

function addComponent() {
  const newComponent = {
    name: 'New Component',
    type: 'container'
  };
  selectComponent(newComponent);
}

// Lifecycle
onMounted(async () => {
  const savedCollapsed = localStorage.getItem('builderSidebarCollapsed');
  if (savedCollapsed !== null) {
    isSidebarCollapsed.value = savedCollapsed === 'true';
  }

  await loadComponentTree();
});
</script>

<style scoped>
.builder-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-secondary);
}

/* Builder header */
.builder-header {
  height: 60px;
  padding: 0 var(--spacing-4);
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.project-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.project-status {
  font-size: var(--font-size-sm);
  padding: var(--spacing-1) var(--spacing-2);
  border-radius: var(--border-radius-full);
  text-transform: capitalize;
}

.project-status.draft {
  background-color: var(--bg-secondary);
  color: var(--text-secondary);
}

.project-status.published {
  background-color: rgba(34, 197, 94, 0.1);
  color: var(--success-color);
}

.header-center {
  display: flex;
  align-items: center;
}

.mode-switcher {
  display: flex;
  gap: var(--spacing-2);
  padding: var(--spacing-1);
  background-color: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
}

.mode-button {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-2) var(--spacing-4);
  border: none;
  background: none;
  color: var(--text-secondary);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: var(--transition-base);
}

.mode-button:hover {
  color: var(--text-primary);
}

.mode-button.active {
  background-color: var(--bg-primary);
  color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

/* Builder content */
.builder-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* Component sidebar */
.component-sidebar {
  width: 280px;
  background-color: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-base);
}

.sidebar-collapsed {
  width: 60px;
}

.sidebar-header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
}

.component-tree {
  flex: 1;
  padding: var(--spacing-4);
  overflow-y: auto;
}

.component-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--border-radius-md);
  color: var(--text-secondary);
  cursor: pointer;
  transition: var(--transition-base);
}

.component-item:hover {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.component-item.active {
  background-color: rgba(99, 102, 241, 0.1);
  color: var(--primary-color);
}

.component-icon {
  font-size: var(--font-size-lg);
}

.empty-state {
  text-align: center;
  padding: var(--spacing-8) var(--spacing-4);
  color: var(--text-secondary);
}

.empty-state i {
  font-size: var(--font-size-3xl);
  margin-bottom: var(--spacing-4);
}

.sidebar-footer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: var(--spacing-2);
}

/* Workspace */
.workspace {
  flex: 1;
  overflow: auto;
  padding: var(--spacing-6);
}

/* Properties panel */
.properties-panel {
  width: 320px;
  background-color: var(--bg-primary);
  border-left: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: var(--spacing-4);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.panel-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
}

.panel-content {
  flex: 1;
  padding: var(--spacing-4);
  overflow-y: auto;
}

.property-group {
  margin-bottom: var(--spacing-4);
}

.property-label {
  display: block;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--spacing-2);
}

.panel-footer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--border-color);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .component-sidebar {
    position: fixed;
    left: 0;
    bottom: 0;
    top: 60px;
    z-index: var(--z-drawer);
    transform: translateX(-100%);
  }

  .component-sidebar.sidebar-collapsed {
    transform: translateX(0);
  }

  .properties-panel {
    position: fixed;
    right: 0;
    bottom: 0;
    top: 60px;
    z-index: var(--z-drawer);
    transform: translateX(100%);
  }

  .properties-panel.show {
    transform: translateX(0);
  }
}
</style> 