<template>
  <div class="flex flex-col h-full bg-dark-800">
    <!-- AI Model Selection -->
    <ModelSelector
      :models="models"
      :model-id="modelId"
      @update:model-id="$emit('update:modelId', $event)"
    />
    
    <!-- Mode Toggle -->
    <ModeSelector
      :mode="mode"
      :modes="['chat', 'build']"
      @update:mode="$emit('update:mode', $event)"
    />
    
    <!-- File Explorer -->
    <FileExplorer
      :files="files"
      :selected-file="selectedFile"
      :show-new-form="showNewFileFormValue"
      :file-types="fileTypes"
      @select-file="$emit('selectFile', $event)"
      @create-file="$emit('createFile', $event)"
    />
    
    <!-- Action Buttons -->
    <div class="mt-auto p-4 border-t border-dark-700 space-y-3">
      <ActionButton
        icon="eye"
        text="Preview App"
        variant="primary"
        :full-width="true"
        :disabled="isLoading"
        @click="$emit('preview')"
      />
      <ActionButton
        icon="undo"
        text="Undo Last Change"
        variant="primary"
        :full-width="true"
        :disabled="isLoading"
        @click="$emit('undo')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ModelSelector, ModeSelector, FileExplorer } from '@/apps/builder/components/molecules/sidebar';
import { ActionButton } from '@/apps/builder/components/atoms';
import type { 
  AIModel, 
  ProjectFile,
  BuilderMode,
  ProjectType 
} from '@/apps/builder/types/builder';

// Local state
const showNewFileFormValue = ref(false);

defineProps<{
  currentProject: ProjectType | null;
  models: AIModel[];
  modelId: string | null;
  files: ProjectFile[];
  selectedFile: ProjectFile | null;
  fileTypes: Record<string, string>;
  isLoading: boolean;
  mode: BuilderMode;
}>();

defineEmits<{
  (e: 'update:modelId', value: string): void;
  (e: 'update:mode', value: BuilderMode): void;
  (e: 'selectFile', file: ProjectFile): void;
  (e: 'createFile', data: { name: string; type: string }): void;
  (e: 'undo'): void;
  (e: 'preview'): void;
}>();
</script>
