<template>
  <div class="h-full flex flex-col">
    <!-- Content that adapts to collapsed state -->
    <div class="flex-1 overflow-y-auto overflow-x-hidden relative">
      <template v-if="!isCollapsed">
        <!-- AI Model Selection -->
        <div class="border-b border-dark-700">
          <ModelSelector
            :models="models"
            :model-id="modelId"
            @update:model-id="$emit('update:modelId', $event)"
          />
        </div>
        
        <!-- Mode Toggle -->
        <div class="border-b border-dark-700">
          <ModeSelector
            :mode="mode"
            :modes="modes"
            @update:mode="$emit('update:mode', $event)"
          />
        </div>

        <!-- File Explorer -->
        <FileExplorer
          :files="files"
          :selected-file="selectedFile"
          :show-new-form="showNewFileFormValue"
          :file-types="fileTypes"
          @select-file="$emit('selectFile', $event)"
          @create-file="$emit('createFile', $event)"
        />
      </template>

      <!-- Collapsed State Icons -->
      <template v-else>
        <div class="py-4 flex flex-col items-center space-y-4">
          <!-- Model Icon -->
          <IconButton
            icon-class="fa-robot"
            size="sm"
            :variant="modelId ? 'primary' : 'default'"
            :title="'AI Model: ' + (selectedModel?.name || 'Select Model')"
          />
          
          <!-- Mode Icons -->
          <div class="space-y-2">
            <IconButton
              v-for="modeOption in modes"
              :key="modeOption"
              :icon-class="getModeIcon(modeOption)"
              :variant="mode === modeOption ? 'primary' : 'default'"
              :title="formatMode(modeOption)"
              size="sm"
              @click="$emit('update:mode', modeOption)"
            />
          </div>

          <!-- Action Icons -->
          <div class="space-y-2">
            <IconButton
              icon-class="fa-eye"
              :variant="currentEditorMode === 'preview' ? 'primary' : 'default'"
              title="Preview App"
              size="sm"
              @click="$emit('preview')"
            />
            <IconButton
              icon-class="fa-undo"
              :variant="'default'"
              title="Undo Last Change"
              size="sm"
              :disabled="isLoading"
              @click="$emit('undo')"
            />
          </div>
        </div>
      </template>
    </div>

    <!-- Action Buttons (only shown when expanded) -->
    <div v-if="!isCollapsed" class="shrink-0 border-t border-dark-700 p-4 space-y-3">
      <ActionButton
        icon="eye"
        text="Preview App"
        :variant="currentEditorMode === 'preview' ? 'primary' : 'default'"
        :full-width="true"
        @click="$emit('preview')"
      />
      <ActionButton
        icon="undo"
        text="Undo Last Change"
        variant="default"
        :full-width="true"
        :disabled="isLoading"
        @click="$emit('undo')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ModelSelector from '@/apps/builder/components/molecules/sidebar/ModelSelector.vue'
import ModeSelector from '@/apps/builder/components/molecules/sidebar/ModeSelector.vue'
import FileExplorer from '@/apps/builder/components/molecules/sidebar/FileExplorer.vue'
import { ActionButton, IconButton } from '@/apps/builder/components/atoms'
import type { 
  AIModel, 
  ProjectFile,
  BuilderMode,
  ProjectType,
  EditorMode 
} from '@/apps/builder/types/builder'

// Local state
const showNewFileFormValue = ref(false)
const modes: BuilderMode[] = ['chat', 'build']

const props = defineProps<{
  currentProject: ProjectType | null
  models: AIModel[]
  modelId: string | null
  files: ProjectFile[]
  selectedFile: ProjectFile | null
  fileTypes: Record<string, string>
  isLoading: boolean
  mode: BuilderMode
  currentEditorMode?: EditorMode
  isCollapsed?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelId', value: string): void
  (e: 'update:mode', value: BuilderMode): void
  (e: 'selectFile', file: ProjectFile): void
  (e: 'createFile', data: { name: string; type: string }): void
  (e: 'undo'): void
  (e: 'preview'): void
}>()

const getModeIcon = (mode: BuilderMode): string => {
  const icons: Record<BuilderMode, string> = {
    chat: 'fa-comments',
    build: 'fa-code'
  }
  return icons[mode] || 'fa-code'
}

const formatMode = (mode: BuilderMode): string => {
  return mode.charAt(0).toUpperCase() + mode.slice(1)
}

// Compute selected model for collapsed state tooltip
const selectedModel = computed(() => 
  props.models.find(m => m.id === props.modelId)
)
</script>

<style scoped>
.w-80 {
  width: 20rem;
}

.w-14 {
  width: 3.5rem;
}

/* Smooth width transition */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Hide scrollbar but allow scrolling */
.overflow-y-auto {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* IE and Edge */
}

.overflow-y-auto::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Opera */
}
</style>
