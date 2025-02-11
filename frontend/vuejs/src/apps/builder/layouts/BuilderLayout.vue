<template>
  <div class="h-screen flex flex-col bg-dark-900">
    <!-- Builder header -->
    <header class="h-[60px] px-4 bg-dark-950 border-b border-dark-700 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <router-link to="/projects" class="p-2 text-gray-400 hover:text-white rounded-lg transition-colors" title="Back to Projects">
          <i class="fas fa-arrow-left"></i>
        </router-link>
        <h1 class="text-lg font-semibold text-white">{{ currentProject?.name || 'Untitled Project' }}</h1>
        <span class="px-2 py-1 text-sm rounded-full capitalize" 
              :class="[currentProject?.status === 'published' ? 'bg-green-500/10 text-green-400' : 'bg-dark-800 text-gray-400']">
          {{ currentProject?.status }}
        </span>
      </div>

      <div class="flex items-center">
        <div class="flex gap-2 p-1 bg-dark-800 rounded-lg">
          <button
            class="flex items-center gap-2 px-4 py-2 rounded-md transition-colors"
            :class="[mode === 'chat' ? 'bg-dark-900 text-primary-400 shadow-sm' : 'text-gray-400 hover:text-white']"
            @click="switchMode('chat')"
          >
            <i class="fas fa-comments"></i>
            Chat Mode
          </button>
          <button
            class="flex items-center gap-2 px-4 py-2 rounded-md transition-colors"
            :class="[mode === 'build' ? 'bg-dark-900 text-primary-400 shadow-sm' : 'text-gray-400 hover:text-white']"
            @click="switchMode('build')"
          >
            <i class="fas fa-magic"></i>
            Build Mode
          </button>
        </div>
      </div>
    </header>

    <!-- Builder content -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Component sidebar -->
      <aside class="w-[280px] bg-dark-950 border-r border-dark-700 flex flex-col transition-all duration-200"
             :class="{ 'w-[60px]': isSidebarCollapsed }">
        <div class="p-4 border-b border-dark-700 flex items-center justify-between">
          <h2 class="text-base font-semibold text-white" v-if="!isSidebarCollapsed">Components</h2>
          <button class="p-2 text-gray-400 hover:text-white rounded-lg transition-colors"
                  @click="toggleSidebar">
            <i class="fas" :class="isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
          </button>
        </div>

        <div class="flex-1 p-4 overflow-y-auto">
          <template v-if="componentTree.length">
            <div
              v-for="component in componentTree"
              :key="component.id"
              class="flex items-center gap-3 p-2 rounded-md text-gray-400 cursor-pointer transition-colors"
              :class="{ 'bg-primary-500/10 text-primary-400': selectedComponent?.id === component.id,
                       'hover:bg-dark-800 hover:text-white': selectedComponent?.id !== component.id }"
              @click="selectComponent(component)"
            >
              <i class="text-lg" :class="getComponentIcon(component.type)"></i>
              <span v-if="!isSidebarCollapsed">{{ component.name }}</span>
            </div>
          </template>
          <div v-else class="text-center py-8 text-gray-400">
            <i class="fas fa-cube text-3xl mb-4"></i>
            <p v-if="!isSidebarCollapsed">No components yet</p>
            <button class="mt-4 px-4 py-2 bg-primary-500 text-white rounded-lg text-sm hover:bg-primary-600 transition-colors"
                    @click="addComponent">
              <i class="fas fa-plus" v-if="isSidebarCollapsed"></i>
              <span v-else>Add Component</span>
            </button>
          </div>
        </div>

        <div class="p-4 border-t border-dark-700 flex gap-2">
          <button
            class="flex-1 px-3 py-2 border border-dark-600 rounded-lg text-gray-400 hover:text-white hover:border-dark-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            @click="undo"
            :disabled="!canUndo"
          >
            <i class="fas fa-undo"></i>
            <span v-if="!isSidebarCollapsed" class="ml-2">Undo</span>
          </button>
          <button
            class="flex-1 px-3 py-2 border border-dark-600 rounded-lg text-gray-400 hover:text-white hover:border-dark-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            @click="redo"
            :disabled="!canRedo"
          >
            <i class="fas fa-redo"></i>
            <span v-if="!isSidebarCollapsed" class="ml-2">Redo</span>
          </button>
        </div>
      </aside>

      <!-- Main workspace -->
      <main class="flex-1 overflow-auto p-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <!-- Properties panel -->
      <aside v-if="selectedComponent && mode === 'build'"
             class="w-[320px] bg-dark-950 border-l border-dark-700 flex flex-col">
        <div class="p-4 border-b border-dark-700 flex items-center justify-between">
          <h2 class="text-base font-semibold text-white">Properties</h2>
          <button class="p-2 text-gray-400 hover:text-white rounded-lg transition-colors"
                  @click="closeProperties">
            <i class="fas fa-times"></i>
          </button>
        </div>

        <div class="flex-1 p-4 overflow-y-auto">
          <div class="space-y-4">
            <div class="space-y-2">
              <label class="block text-sm text-gray-400">Name</label>
              <input type="text"
                     v-model="selectedComponent.name"
                     class="w-full px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white focus:border-primary-500 transition-colors" />
            </div>
            <!-- Add more property fields as needed -->
          </div>
        </div>

        <div class="p-4 border-t border-dark-700">
          <button class="w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors">
            Apply Changes
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
.fade-enter-active,
.fade-leave-active {
  transition-property: opacity;
  transition-duration: 200ms;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>