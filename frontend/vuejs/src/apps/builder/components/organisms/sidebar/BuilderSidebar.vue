<template>
  <div class="flex flex-col h-full bg-dark-800">
    <ProjectHeader :project-name="currentProject?.name" />
    
    <ModelSelector
      :models="models"
      :model-id="modelId"
      @update:model-id="$emit('update:modelId', $event)"
    />
    
    <ModeSelector
      :mode="mode"
      :modes="['chat', 'build']"
      @update:mode="$emit('update:mode', $event)"
    />
    
    <FileExplorer
      :files="files"
      :selected-file="selectedFile"
      :show-new-form="showNewFileFormValue"
      :file-types="fileTypes"
      @select-file="$emit('selectFile', $event)"
      @create-file="$emit('createFile', $event)"
    />
    
    <div class="mt-auto p-4 border-t border-dark-700">
      <IconButton
        icon-class="fa-undo"
        text="Undo"
        variant="primary"
        class="w-full justify-center"
        :disabled="isLoading"
        @click="$emit('undo')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ProjectHeader } from '@/apps/builder/components/molecules/sidebar';
import { ModelSelector } from '@/apps/builder/components/molecules/sidebar';
import { ModeSelector } from '@/apps/builder/components/molecules/sidebar';
import { FileExplorer } from '@/apps/builder/components/molecules/sidebar';
import { IconButton } from '@/apps/builder/components/atoms';
import type { 
  AIModel, 
  ProjectFile,
  BuilderMode,
  ProjectType 
} from '@/apps/builder/types/builder';

// Local state
const showNewFileFormValue = ref(false);
const mode = ref<BuilderMode>('chat');

defineProps<{
  currentProject: ProjectType | null;
  models: AIModel[];
  modelId: string | null;
  files: ProjectFile[];
  selectedFile: ProjectFile | null;
  fileTypes: Record<string, string>;
  isLoading: boolean;
}>();

defineEmits<{
  (e: 'update:modelId', value: string): void;
  (e: 'update:mode', value: BuilderMode): void;
  (e: 'selectFile', file: ProjectFile): void;
  (e: 'createFile', data: { name: string; type: string }): void;
  (e: 'undo'): void;
}>();
</script>
