<!--
  BuilderWorkspace.vue - Project Editing Interface
  
  This component is responsible for:
  1. Loading an existing project's files and data
  2. Supporting chat & build modes for AI interaction
  3. Editing project files through AI assistance
-->
<template>
  <div class="relative">
    <!-- Fixed position account balance display -->
    <AccountBalanceDisplay />
    
    <BuilderLayout 
      storage-key="builderWorkspaceSidebarCollapsed"
      :navigation-items="navigationItems"
    >
      <!-- Centered navbar content: project name and description -->
      <template #navbar-center>
        <div class="flex flex-col items-center text-center select-none">
          <div class="relative flex items-center gap-2">
            <span class="text-sm font-semibold bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent truncate max-w-[50vw]">
              {{ navbarNameSanitized }}
            </span>
          </div>
          <div v-if="currentProject && currentProject.description" class="mt-0.5 text-[11px] text-gray-400/90 truncate max-w-[60vw]">
            {{ navbarDescSanitized }}
          </div>
        </div>
      </template>
      <!-- Sidebar Content (removed as per request) -->
      <template #sidebar-content>
        <!-- Intentionally left empty to remove all sidebar UI -->
      </template>

      <!-- Premium Dark-themed Main Content Area - Matching Home Page -->
      <div class="flex flex-col h-screen max-h-screen w-full overflow-x-hidden overflow-y-hidden bg-[#050508] relative">
        <WorkspaceBackground />
        
        <!-- Premium top accent line -->
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent z-20"></div>

        <!-- Enhanced Error State Display -->
        <WorkspaceError v-if="store.error" :error="store.error" @retry="retryProjectLoad" />
        
        <!-- Main Layout: Navigation above, Chat Input always at bottom -->
        <div v-else class="flex-1 flex flex-col h-full min-h-0 overflow-hidden relative z-10">
          <!-- Navigation Area (scrollable) -->
          <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
            <!-- Conversation Panel (when there are messages) -->
            <div v-if="hasConversation" class="flex-1 min-h-0 flex flex-col overflow-hidden">
              <!-- Breadcrumb Header -->
              <div class="shrink-0 px-6 py-3 border-b border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl">
                <div class="flex items-center justify-between">
                  <!-- Breadcrumb navigation -->
                  <div class="flex items-center gap-2 text-sm">
                    <button 
                      @click="handleBackToApps"
                      class="text-white/50 hover:text-white transition-colors"
                    >
                      Apps
                    </button>
                    <template v-if="selectedApp">
                      <i class="fas fa-chevron-right text-[10px] text-white/30"></i>
                      <button 
                        @click="handleBackToApp"
                        class="text-white/50 hover:text-white transition-colors"
                      >
                        {{ selectedApp.displayName }}
                      </button>
                    </template>
                    <template v-if="store.selectedFile">
                      <i class="fas fa-chevron-right text-[10px] text-white/30"></i>
                      <span class="text-white/90 font-medium">{{ getDisplayName(store.selectedFile.path) }}</span>
                    </template>
                  </div>
                  
                  <!-- Close conversation button -->
                  <button
                    @click="handleCloseConversation"
                    class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.05] border border-white/[0.08] hover:bg-white/[0.08] hover:border-white/[0.12] transition-all text-sm text-white/70 hover:text-white"
                  >
                    <i class="fas fa-times text-xs"></i>
                    <span>Close</span>
                  </button>
                </div>
              </div>
              
              <!-- Chat Conversation Area -->
              <div class="flex-1 min-h-0 overflow-y-auto">
                <ChatConversation
                  :messages="ensureValidMessages(store.conversation || [])"
                  :is-processing="store.isProcessing"
                  @use-example="handleExamplePrompt"
                />
              </div>
            </div>
            
            <!-- Navigation Views (when no conversation or minimized) -->
            <div v-else class="flex-1 min-h-0 overflow-hidden">
              <!-- Split Screen Layout: Apps List + Detail View -->
              <div class="h-full p-4 sm:p-6 lg:p-8 flex gap-4">
                <!-- Left Side: Apps List (1/3 width) -->
                <div class="w-1/3 flex flex-col min-h-0">
                  <div class="group relative flex-1 min-h-0">
                    <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-2xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-500"></div>
                    
                    <div class="relative h-full rounded-xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden flex flex-col">
                      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                      <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
                      <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
                    
                      <AppsList
                        :files="store.files || []"
                        @select-app="handleSelectApp"
                        @create-app="handleCreateAppFromGallery"
                        class="flex-1 min-h-0"
                      />
                    </div>
                  </div>
                </div>

                <!-- Right Side: App Detail View (2/3 width) -->
                <div class="w-2/3 flex flex-col min-h-0">
                  <div class="group relative flex-1 min-h-0">
                    <div class="absolute -inset-1 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-2xl blur-xl opacity-50 group-hover:opacity-70 transition-opacity duration-500"></div>
                    
                    <div class="relative h-full rounded-xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden flex flex-col">
                      <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
                      <div class="absolute -bottom-20 -right-20 w-40 h-40 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
                      <div class="absolute -top-20 -left-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
                    
                      <!-- App Detail View (when app selected) -->
                      <AppDetailView
                        v-if="selectedApp"
                        :app="selectedApp"
                        @back="handleBackToList"
                        @select-file="handleFileSelectFromDetail"
                        @create-file="handleFileCreate"
                        @category-change="handleCategoryChange"
                        class="flex-1 min-h-0"
                      />
                      
                      <!-- Empty State (when no app selected) -->
                      <div v-else class="flex-1 flex items-center justify-center p-8">
                        <div class="text-center max-w-md">
                          <div class="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 mb-6">
                            <i class="fas fa-arrow-left text-violet-400 text-3xl"></i>
                          </div>
                          <h3 class="text-2xl font-semibold text-white/90 mb-3">Select an App</h3>
                          <p class="text-white/50 leading-relaxed">
                            Choose an app from the left to view its pages, blocks, and other files. You can then edit them or create new ones.
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Persistent Chat Input Section (always at bottom) -->
          <div class="shrink-0 relative">
            <!-- Background with subtle gradient -->
            <div class="bg-gradient-to-t from-[#050508] via-[#050508]/98 to-[#050508]/95 backdrop-blur-xl border-t border-white/[0.03]">
              <div class="max-w-4xl mx-auto px-4 sm:px-6 py-5">
                <!-- Main Input Card -->
                <div class="group relative">
                  <!-- Card container with subtle shadow on focus -->
                  <div class="relative rounded-2xl border bg-[#0a0a0f]/70 backdrop-blur-xl overflow-hidden transition-all duration-200"
                       :class="prompt.trim() ? 'border-white/[0.08] shadow-lg shadow-black/20' : 'border-white/[0.04] group-focus-within:border-white/[0.06] group-focus-within:shadow-md group-focus-within:shadow-black/10'">
                    
                    <!-- Controls Row - Reorganized: Files (left) → Model (middle) → Ask/Edit (right) -->
                    <div class="flex items-center gap-2 px-4 py-2.5 border-b border-white/[0.03]">
                      <!-- File Context Picker - Now supports multiple file selection -->
                      <div class="relative" ref="filePickerRef">
                        <button
                          @click="toggleFilePicker"
                          class="flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-xs font-medium"
                          :class="selectedContextFiles.length > 0
                            ? 'bg-white/[0.08] text-white/90 hover:bg-white/[0.12] border border-white/[0.08]' 
                            : 'bg-white/[0.02] text-white/40 hover:bg-white/[0.04] hover:text-white/60 border border-white/[0.04]'"
                        >
                          <i :class="selectedContextFiles.length > 0 ? 'fas fa-file-code' : 'fas fa-plus'" class="text-[10px]"></i>
                          <span v-if="selectedContextFiles.length === 1" class="max-w-[120px] truncate">{{ getDisplayName(selectedContextFiles[0].path) }}</span>
                          <span v-else-if="selectedContextFiles.length > 1" class="max-w-[120px] truncate">{{ selectedContextFiles.length }} files</span>
                          <span v-else>Add context</span>
                          <i class="fas fa-chevron-down text-[8px] opacity-50 transition-transform duration-200" :class="{ 'rotate-180': isFilePickerOpen }"></i>
                        </button>
                        
                        <!-- File Picker Dropdown with multi-select -->
                        <div
                          v-if="isFilePickerOpen"
                          class="absolute top-full left-0 mt-2 w-72 max-h-80 flex flex-col bg-[#0a0a0f]/98 backdrop-blur-xl border border-white/[0.06] rounded-xl shadow-2xl shadow-black/60 z-50 overflow-hidden"
                        >
                          <div class="flex-1 overflow-y-auto p-2">
                            <!-- Clear all button -->
                            <button
                              v-if="selectedContextFiles.length > 0"
                              @click="clearAllFileSelections"
                              class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs text-white/50 hover:bg-white/[0.04] hover:text-white/80 transition-colors mb-2 border-b border-white/[0.04] pb-3"
                            >
                              <i class="fas fa-times text-[10px]"></i>
                              <span>Clear all ({{ selectedContextFiles.length }})</span>
                            </button>
                            
                            <!-- Files grouped by category with checkboxes -->
                            <div v-if="selectedApp" class="space-y-1">
                              <!-- Pages -->
                              <div v-if="appPages.length > 0">
                                <div class="px-3 py-1.5 text-[10px] font-semibold text-white/25 uppercase tracking-wider">Pages</div>
                                <button
                                  v-for="file in appPages"
                                  :key="file.path"
                                  @click="toggleFileContext(file)"
                                  class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs transition-all"
                                  :class="isFileSelected(file.path)
                                    ? 'bg-white/[0.08] text-white/90 border border-white/[0.10]' 
                                    : 'text-white/50 hover:bg-white/[0.03] hover:text-white/70 border border-transparent'"
                                >
                                  <!-- Checkbox -->
                                  <div class="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0"
                                    :class="isFileSelected(file.path)
                                      ? 'bg-white/[0.15] border-white/[0.25]'
                                      : 'bg-white/[0.02] border-white/[0.10]'"
                                  >
                                    <i v-if="isFileSelected(file.path)" class="fas fa-check text-[8px] text-white"></i>
                                  </div>
                                  <i class="fas fa-window-maximize text-[10px] text-white/40"></i>
                                  <span class="truncate flex-1">{{ getDisplayName(file.path) }}</span>
                                </button>
                              </div>
                              
                              <!-- Blocks -->
                              <div v-if="appBlocks.length > 0">
                                <div class="px-3 py-1.5 text-[10px] font-semibold text-white/25 uppercase tracking-wider mt-2">Blocks</div>
                                <button
                                  v-for="file in appBlocks"
                                  :key="file.path"
                                  @click="toggleFileContext(file)"
                                  class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs transition-all"
                                  :class="isFileSelected(file.path)
                                    ? 'bg-white/[0.08] text-white/90 border border-white/[0.10]' 
                                    : 'text-white/50 hover:bg-white/[0.03] hover:text-white/70 border border-transparent'"
                                >
                                  <!-- Checkbox -->
                                  <div class="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0"
                                    :class="isFileSelected(file.path)
                                      ? 'bg-white/[0.15] border-white/[0.25]'
                                      : 'bg-white/[0.02] border-white/[0.10]'"
                                  >
                                    <i v-if="isFileSelected(file.path)" class="fas fa-check text-[8px] text-white"></i>
                                  </div>
                                  <i class="fas fa-puzzle-piece text-[10px] text-white/40"></i>
                                  <span class="truncate flex-1">{{ getDisplayName(file.path) }}</span>
                                </button>
                              </div>
                              
                              <!-- Data -->
                              <div v-if="appStores.length > 0">
                                <div class="px-3 py-1.5 text-[10px] font-semibold text-white/25 uppercase tracking-wider mt-2">Data</div>
                                <button
                                  v-for="file in appStores"
                                  :key="file.path"
                                  @click="toggleFileContext(file)"
                                  class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-left text-xs transition-all"
                                  :class="isFileSelected(file.path)
                                    ? 'bg-white/[0.08] text-white/90 border border-white/[0.10]' 
                                    : 'text-white/50 hover:bg-white/[0.03] hover:text-white/70 border border-transparent'"
                                >
                                  <!-- Checkbox -->
                                  <div class="w-4 h-4 rounded border flex items-center justify-center flex-shrink-0"
                                    :class="isFileSelected(file.path)
                                      ? 'bg-white/[0.15] border-white/[0.25]'
                                      : 'bg-white/[0.02] border-white/[0.10]'"
                                  >
                                    <i v-if="isFileSelected(file.path)" class="fas fa-check text-[8px] text-white"></i>
                                  </div>
                                  <i class="fas fa-database text-[10px] text-white/40"></i>
                                  <span class="truncate flex-1">{{ getDisplayName(file.path) }}</span>
                                </button>
                              </div>
                              
                              <!-- Empty state -->
                              <div v-if="appPages.length === 0 && appBlocks.length === 0 && appStores.length === 0" class="px-3 py-4 text-center text-xs text-white/30">
                                No files in this app yet
                              </div>
                            </div>
                            
                            <!-- No app selected -->
                            <div v-else class="px-3 py-4 text-center text-xs text-white/30">
                              Select an app first
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <!-- Divider -->
                      <div class="w-px h-5 bg-white/[0.04]"></div>
                      
                      <!-- Model Selector - Now in middle -->
                      <div class="min-w-[160px] max-w-[200px]">
                        <ModelSelector 
                          :models="store.availableModels || []"
                          :model-id="store.selectedModelId"
                          :mode="store.mode || 'chat'"
                          @update:model-id="handleModelSelect"
                          compact
                        />
                      </div>
                      
                      <!-- Spacer -->
                      <div class="flex-1"></div>
                      
                      <!-- Mode Toggle - Now on right side -->
                      <div class="flex items-center bg-white/[0.02] rounded-lg p-0.5 border border-white/[0.04]">
                        <button
                          @click="handleModeSwitch('chat')"
                          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
                          :class="store.mode === 'chat' 
                            ? 'bg-white/[0.08] text-white/90 shadow-sm' 
                            : 'text-white/40 hover:text-white/60 hover:bg-white/[0.03]'"
                        >
                          <i class="fas fa-comments text-[10px]"></i>
                          <span>Ask</span>
                        </button>
                        <button
                          @click="handleModeSwitch('build')"
                          class="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200"
                          :class="store.mode === 'build' 
                            ? 'bg-white/[0.08] text-white/90 shadow-sm' 
                            : 'text-white/40 hover:text-white/60 hover:bg-white/[0.03]'"
                        >
                          <i class="fas fa-magic text-[10px]"></i>
                          <span>Edit</span>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Input Area -->
                    <div class="relative">
                      <!-- Textarea -->
                      <textarea
                        ref="promptTextarea"
                        v-model="prompt"
                        :placeholder="promptPlaceholder"
                        @keydown.enter.exact.prevent="handlePrompt"
                        @keydown.enter.shift.exact="() => {}"
                        @input="autoResizeTextarea"
                        :disabled="store.isProcessing"
                        rows="1"
                        class="w-full bg-transparent text-white/90 placeholder-white/30 text-sm pl-4 pr-14 py-3.5 resize-none focus:outline-none leading-relaxed transition-all duration-200 focus:placeholder-white/40"
                        style="min-height: 52px; max-height: 160px;"
                      ></textarea>
                      
                      <!-- Send Button -->
                      <div class="absolute right-3 bottom-3">
                        <button
                          @click="handlePrompt"
                          :disabled="!prompt.trim() || store.isProcessing"
                          class="flex items-center justify-center w-9 h-9 rounded-xl transition-all duration-200"
                          :class="prompt.trim() && !store.isProcessing
                            ? 'bg-white/[0.12] text-white hover:bg-white/[0.18] active:bg-white/[0.15]'
                            : 'bg-white/[0.03] text-white/15 cursor-not-allowed'"
                        >
                          <i v-if="store.isProcessing" class="fas fa-circle-notch fa-spin text-xs"></i>
                          <i v-else class="fas fa-arrow-up text-xs"></i>
                        </button>
                      </div>
                    </div>
                    
                    <!-- Footer hints -->
                    <div class="flex items-center justify-between px-4 py-2 border-t border-white/[0.02]">
                      <div class="text-[11px] text-white/25 flex items-center gap-2 flex-1 min-w-0">
                        <span v-if="store.mode === 'build' && selectedContextFiles.length === 0" class="flex items-center gap-1.5 text-white/30">
                          <i class="fas fa-info-circle text-[9px]"></i>
                          <span>Select a file to make changes</span>
                        </span>
                        <span v-else-if="selectedContextFiles.length > 0" class="flex items-center gap-2 flex-wrap">
                          <span class="flex items-center gap-1.5">
                            <i class="fas fa-file-code text-[9px] text-white/30"></i>
                            <span class="font-medium text-white/25">Context:</span>
                          </span>
                          <span v-if="selectedContextFiles.length === 1" class="text-white/35">{{ getDisplayName(selectedContextFiles[0].path) }}</span>
                          <span v-else class="flex items-center gap-1">
                            <span class="truncate max-w-[120px] text-white/35">{{ getDisplayName(selectedContextFiles[0].path) }}</span>
                            <span class="text-white/40">+{{ selectedContextFiles.length - 1 }} more</span>
                          </span>
                        </span>
                      </div>
                      <div class="text-[11px] text-white/20 flex items-center gap-3 flex-shrink-0">
                        <span class="flex items-center gap-1">
                          <kbd class="px-1.5 py-0.5 bg-white/[0.02] rounded text-[9px] font-medium border border-white/[0.04]">⏎</kbd>
                          <span>send</span>
                        </span>
                        <span class="flex items-center gap-1">
                          <kbd class="px-1.5 py-0.5 bg-white/[0.02] rounded text-[9px] font-medium border border-white/[0.04]">⇧⏎</kbd>
                          <span>new line</span>
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </BuilderLayout>
    <!-- New App Modal -->
    <NewAppModal
      v-model="showNewAppModal"
      :submitting="isCreatingApp"
      @submit="handleCreateAppSubmit"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import useChatMode from '../composables/useChatMode'
import { useProjectStore } from '../stores/projectStore'
import { AgentService } from '../services/agentService'
import { FileService } from '../services/fileService'
import { PreviewService } from '../services/previewService'
import { BuilderCreationService } from '../services/builderCreationService'
import { VersionControlService } from '../services/versionControlService'
import { RouterUpdateService } from '../services/routerUpdateService'
import { useAuthStore } from '@/shared/stores/auth'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useBalanceStore } from '@/shared/stores/balance'
import { useNotification } from '@/shared/composables/useNotification'

// Builder Components
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import { AccountBalanceDisplay } from '../components/molecules'

// Atomic Components
import { 
  WorkspaceChat,
  WorkspaceBackground,
  WorkspaceError,
} from '../components/organisms/workspace'
import { ChatConversation } from '../components/organisms/chat'
import AppsList from '../components/organisms/workspace/AppsList.vue'
import AppDetailView from '../components/organisms/workspace/AppDetailView.vue'
import NewAppModal from '../components/organisms/workspace/NewAppModal.vue'
import ModelSelector from '../components/molecules/sidebar/ModelSelector.vue'
// Set component name
defineOptions({ name: 'BuilderWorkspace' })

// Types
import type { ProjectFile, BuilderMode } from '../types/components'
import type { AIMessage } from '../types/index'

// Ensure all services use the shared API client with proper timeout configurations
const AI_TIMEOUT = 90000 // 90 seconds for AI processing

const route = useRoute()
const router = useRouter()
const store = useAgentStore()
const projectStore = useProjectStore()
const projectId = ref<string>('')
const { 
  createFile, 
  loadModels,
  applyCode 
} = useBuilderMode()
const {} = useChatMode()

// Constants
const fileTypes = {
  'vue': 'Vue Component',
  'ts': 'TypeScript',
  'js': 'JavaScript',
  'css': 'CSS',
  'html': 'HTML',
  'json': 'JSON',
  'md': 'Markdown'
}

// Simple creation flows for non-technical users via AppGallery
// New App modal state
const showNewAppModal = ref(false)
const isCreatingApp = ref(false)

// Open the styled New App modal
async function handleCreateAppFromGallery() {
  showNewAppModal.value = true
}

// Submit handler for New App modal
async function handleCreateAppSubmit(payload: { name: string; description: string }) {
  try {
    if (!projectId.value) return
    isCreatingApp.value = true

    const result = await BuilderCreationService.createAppFromGallery(
      projectId.value,
      payload.name,
      payload.description || ''
    )

    if (result.success) {
      // Close modal and refresh files to show the new app
      showNewAppModal.value = false
      await loadProjectFiles(true)
      const { showNotification } = useNotification()
      showNotification({
        type: 'success',
        message: result.message || 'App created successfully',
        duration: 3000
      })
    } else {
      console.error('Failed to create app:', result.error)
      const { showNotification } = useNotification()
      showNotification({
        type: 'error',
        message: result.error || 'Failed to create app',
        duration: 5000
      })
    }
  } catch (e) {
    console.error('Error creating app from gallery:', e)
    const { showNotification } = useNotification()
    showNotification({
      type: 'error',
      message: 'Unexpected error creating app',
      duration: 5000
    })
  } finally {
    isCreatingApp.value = false
  }
}

// Version history state and actions
const versionHistory = ref<Array<Record<string, any>>>([])
const selectedVersionHash = ref<string>('')
const isLoadingVersions = ref<boolean>(false)

async function loadVersionHistory() {
  if (!projectId.value) return
  try {
    isLoadingVersions.value = true
    const res = await AgentService.getVersionHistory(projectId.value)
    // Support either versions or commits shapes
    const list = (res && (res as any).versions) || (res as any).commits || []
    versionHistory.value = Array.isArray(list) ? list : []
  } catch (e) {
    console.error('Failed to load version history:', e)
  } finally {
    isLoadingVersions.value = false
  }
}

async function onVersionSelect() {
  try {
    const hash = selectedVersionHash.value
    if (!hash || !projectId.value) return
    const res = await AgentService.resetToVersion(projectId.value, hash)
    if ((res as any)?.success !== false) {
      await handleVersionReset({ hash })
      await loadVersionHistory()
      // Clear selection after reset
      selectedVersionHash.value = ''
    }
  } catch (e) {
    console.error('Failed to reset to selected version:', e)
  }
}

// Local state
const prompt = ref('')
const showAppsInMain = ref(true)
const selectedApp = ref<any>(null)
const selectedCategory = ref<{ key: string; label: string } | null>(null)
const isFilePickerOpen = ref(false)
const filePickerRef = ref<HTMLElement | null>(null)
const promptTextarea = ref<HTMLTextAreaElement | null>(null)
const selectedContextFiles = ref<ProjectFile[]>([])

// Auto-resize textarea based on content
function autoResizeTextarea() {
  if (!promptTextarea.value) return
  promptTextarea.value.style.height = 'auto'
  const scrollHeight = promptTextarea.value.scrollHeight
  const maxHeight = 160
  promptTextarea.value.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

// Computed: check if there's an active conversation
const hasConversation = computed(() => {
  return store.conversation && store.conversation.length > 0
})

// Helper to check if file is a barrel file
function isBarrelFile(path: string): boolean {
  const filename = path.split('/').pop()?.toLowerCase() || ''
  return filename === 'index.ts' || filename === 'index.js' || filename === 'index.vue'
}

// Computed: files in the selected app categorized
const appPages = computed(() => {
  if (!selectedApp.value?.files) return []
  return selectedApp.value.files.filter((f: ProjectFile) => 
    /\/views\//i.test(f.path) && !isBarrelFile(f.path)
  )
})

const appBlocks = computed(() => {
  if (!selectedApp.value?.files) return []
  return selectedApp.value.files.filter((f: ProjectFile) => 
    /\/components\//i.test(f.path) && !isBarrelFile(f.path)
  )
})

const appStores = computed(() => {
  if (!selectedApp.value?.files) return []
  return selectedApp.value.files.filter((f: ProjectFile) => 
    (/\/stores\//i.test(f.path) || /store\.(ts|js)$/i.test(f.path)) && !isBarrelFile(f.path)
  )
})

// Navigation items for sidebar
const navigationItems: any[] = [] // Empty array to remove sidebar navigation buttons

// Computed properties
const currentProject = computed(() => {
  return projectStore.currentProject || null
})

const promptExamplesComputed = computed(() => {
  return [] // Return empty array for examples
})

// Display name for the Project Web App title
const projectTitle = computed(() => {
  const name = currentProject.value && (currentProject.value as any).name
  return name && String(name).trim() ? String(name) : ''
})

// Sanitized project title for display (remove 'spacex')
const sanitizedProjectTitle = computed(() => {
  const title = projectTitle.value || ''
  const cleaned = title.replace(/spacex/ig, '').trim()
  return cleaned || ''
})

// Sanitized navbar project name and description (remove 'spacex')
const navbarNameSanitized = computed(() => {
  const raw = currentProject.value && (currentProject.value as any).name
    ? String((currentProject.value as any).name)
    : ''
  return raw.trim()
})

const navbarDescSanitized = computed(() => {
  const raw = currentProject.value && (currentProject.value as any).description
    ? String((currentProject.value as any).description)
    : ''
  return raw.trim()
})

// Refresh files and clear any selection on version reset
async function handleVersionReset(version: Record<string, any>) {
  try {
    console.debug('Version reset to:', version)
    await loadProjectFiles(true)
    // Optionally clear selected file to avoid stale content
    if (typeof store.setSelectedFile === 'function') {
      store.setSelectedFile(null)
    }
  } catch (e) {
    console.error('Error handling version reset:', e)
  }
}

// Helper to get friendly display name from file path
function getDisplayName(path: string): string {
  if (!path) return ''
  const parts = path.split('/')
  const filename = parts[parts.length - 1]
  // Remove extension and return friendly name
  return filename.replace(/\.(vue|ts|js|tsx|jsx)$/, '')
}

// Helper to determine item kind from path (Page, Block, or Item)
function getItemKind(path: string): string {
  if (!path) return 'item'
  if (/\/views\//i.test(path)) return 'page'
  if (/\/components\//i.test(path)) return 'block'
  if (/\/stores\//i.test(path)) return 'data store'
  return 'item'
}

const promptPlaceholder = computed(() => {
  if (store.mode === 'chat') {
    if (store.selectedFile) {
      const displayName = getDisplayName(store.selectedFile.path)
      const itemKind = getItemKind(store.selectedFile.path)
      return `Ask me anything about "${displayName}" or your project...`
    }
    return 'Ask me anything about your project or get help with your app...'
  } else {
    if (store.selectedFile) {
      const displayName = getDisplayName(store.selectedFile.path)
      const itemKind = getItemKind(store.selectedFile.path)
      return `Describe the changes you want to make to "${displayName}"...`
    }
    return 'Select a page or block to start making changes...'
  }
})

// Helper function to get just the filename
function getFileName(path: string): string {
  if (!path) return 'this file'
  const parts = path.split('/')
  return parts[parts.length - 1]
}

// Methods
function ensureValidMessages(messages: any[]): AIMessage[] {
  if (!messages || !Array.isArray(messages)) {
    return []
  }
  
  // Filter out system messages related to file switching in all modes
  const filteredMessages = messages.filter(m => {
    // Remove all system messages related to file switching
    if (m && m.role === 'system') {
      // Filter out messages about file switching, mode switching or file availability
      if (m.content && (
        m.content.includes('Switched to file:') || 
        m.content.includes('Switched to build mode') ||
        m.content.includes('previously selected file')
      )) {
        return false;
      }
    }
    return true;
  });
  
  const validMessages = filteredMessages
    .filter(m => m && typeof m === 'object' && m.role)
    .map(m => {
      // Ensure content is a valid string
      let content = m.content || '';
      
      // Generate a new id if not present to force proper rendering
      const messageId = m.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
      
      return {
        role: m.role,
        content: content,
        code: m.code || '',
        timestamp: m.timestamp || new Date().toISOString(),
        id: messageId
      };
    }) as AIMessage[];
  
  return validMessages
}

// Create a git commit after successful code changes
function createCommitFromPrompt(filePath: string, prompt: string) {
  if (!projectId.value || !filePath) return;
  
  // Use the version control service to handle commits in the background
  VersionControlService.commitAfterFileOperation(
    projectId.value,
    filePath,
    prompt
  );
}

async function handlePrompt() {
  if (!prompt.value.trim()) return
  
  try {
    if (!store.selectedModelId) {
      return
    }
    
    const timestamp = new Date().toISOString()
    
    // Get payments store for updating balance
    const balanceStore = useBalanceStore()
    
    // Mark that a transaction is about to happen to ensure fresh balance data
    balanceStore.beginTransaction()
    
    // Check if we have a project ID
    if (!projectId.value) {
      return
    }
    
    // Set processing flag TRUE at the start
    store.setProcessing(true)
    
    // Add the user message to the conversation immediately
    store.addMessage({
      role: 'user',
      content: prompt.value,
      timestamp: timestamp,
      id: `user-${Date.now()}`
    })
    
    // For build mode, file selection is required
    if (store.mode === 'build' && !store.selectedFile) {
      return
    }
    
    // Get user auth status before making request
    const isUserAuthenticated = await useAuthStore().validateAuth()
    if (!isUserAuthenticated) {
      return
    }
    
    if (store.mode === 'build') {
      // Check for missing required values
      if (!projectId.value) {
        return
      }
      
      if (!store.selectedFile) {
        return
      }
      
      // Determine file type for specialized handling
      const fileExtension = store.selectedFile.path.split('.').pop()?.toLowerCase() || ''
      const isCSS = fileExtension === 'css' || store.selectedFile.type === 'css'
      const isHTML = fileExtension === 'html' || store.selectedFile.type === 'html'
      
      if (isCSS) {
        try {
          // For CSS files, use specialized stylesheet generator function
          const response = await AgentService.generateStylesheet({
            prompt: prompt.value,
            projectId: projectId.value,
            filePath: store.selectedFile.path,
            model: store.selectedModelId,
            onProgress: (progress) => {
              // Update UI with progress - no notification needed
            }
          });
          
          // Ensure we got a valid response
          if (response && (response.response || response.code)) {
            // Get the content from either response or code field
            const cssContent = response.response || response.code || '';
            
            if (!cssContent.trim()) {
              store.addMessage({
                role: 'assistant',
                content: 'No stylesheet changes were generated. Please try a different prompt.',
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              });
              return;
            }
            
            // Apply the generated code
            try {
              await applyCode({
                code: cssContent,
                file: store.selectedFile,
                projectId: projectId.value
              });
              
              const simpleSummary = `Changes successfully applied to ${store.selectedFile.path}`;
              
              // Add assistant message to conversation
              store.addMessage({
                role: 'assistant',
                content: simpleSummary,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              });
              
              // Create a git commit for the CSS changes
              createCommitFromPrompt(store.selectedFile.path, prompt.value);
            } catch (applyError) {
              console.error('Error applying stylesheet changes:', applyError);
              store.addMessage({
                role: 'assistant',
                content: `Failed to apply stylesheet changes to ${store.selectedFile.path}: ${applyError instanceof Error ? applyError.message : 'Unknown error'}`,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              });
            }
          } else {
            store.addMessage({
              role: 'assistant',
              content: 'No stylesheet changes were generated. Please try a different prompt.',
              timestamp: new Date().toISOString(),
              id: `assistant-response-${Date.now()}`
            });
          }
        } catch (cssError) {
          console.error('Error generating stylesheet:', cssError);
          
          store.addMessage({
            role: 'assistant',
            content: `Error generating stylesheet: ${cssError instanceof Error ? cssError.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          });
        }
      } else if (isHTML) {
        try {
          // Ensure the file path is correctly formatted for HTML files
          let formattedPath = store.selectedFile.path;
          if (!formattedPath.includes('/templates/') && !formattedPath.startsWith('templates/')) {
            formattedPath = `templates/${formattedPath.replace(/^\//, '')}`;
          }
          
          // Call the AI service to generate code - will use template endpoint in agentService
          const response = await AgentService.generateCode(
            projectId.value,
            {
              prompt: prompt.value,
              model: store.selectedModelId,
              mode: 'build',
              file_path: formattedPath
            }
          )
          
          // Apply the generated code automatically if available
          if (response && response.code) {
            try {
              await applyCode({
                code: response.code,
                file: store.selectedFile,
                projectId: projectId.value
              })
              
              const simpleSummary = `Changes successfully applied to ${store.selectedFile.path}`;
              
              store.addMessage({
                role: 'assistant',
                content: simpleSummary,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
              
              // Create a git commit for the HTML changes
              createCommitFromPrompt(store.selectedFile.path, prompt.value);
            } catch (applyError) {
              console.error('Error applying HTML template:', applyError)
              
              store.addMessage({
                role: 'assistant',
                content: `Failed to apply changes to ${store.selectedFile.path}: ${applyError instanceof Error ? applyError.message : 'Unknown error'}`,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
            }
          } else {
            store.addMessage({
              role: 'assistant',
              content: 'No HTML template was generated. Please try a different prompt.',
              timestamp: new Date().toISOString(),
              id: `assistant-response-${Date.now()}`
            })
          }
        } catch (htmlError) {
          console.error('Error generating HTML template:', htmlError)
          
          store.addMessage({
            role: 'assistant',
            content: `Error generating HTML template: ${htmlError instanceof Error ? htmlError.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
        }
      } else {
        try {
          // Call the AI service to generate code
          const response = await AgentService.generateCode(
            projectId.value,
            {
              prompt: prompt.value,
              model: store.selectedModelId,
              mode: 'build',
              file_path: store.selectedFile.path
            }
          )
          
          // Apply the generated code automatically
          if (response && response.code) {
            try {
              // Apply the generated code automatically
              await applyCode({
                code: response.code,
                file: store.selectedFile,
                projectId: projectId.value
              })
              
              // Add only a single success message instead of two
              const simpleSummary = `Changes successfully applied to ${store.selectedFile.path}`;
              
              store.addMessage({
                role: 'assistant',
                content: simpleSummary,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
              
              // Create a git commit for the applied changes
              createCommitFromPrompt(store.selectedFile.path, prompt.value);
            } catch (applyError) {
              console.error('Error applying generated code:', applyError)
              
              // Just add a single error message
              store.addMessage({
                role: 'assistant',
                content: `Failed to apply changes to ${store.selectedFile.path}: ${applyError instanceof Error ? applyError.message : 'Unknown error'}`,
                timestamp: new Date().toISOString(),
                id: `assistant-response-${Date.now()}`
              })
            }
          } else {
            // No code was generated, just show the response
            store.addMessage({
              role: 'assistant',
              content: 'No code changes were generated. Please try a different prompt.',
              timestamp: new Date().toISOString(),
              id: `assistant-response-${Date.now()}`
            })
          }
        } catch (buildError) {
          console.error('Error in build mode:', buildError)
          
          // Add error message to conversation
          store.addMessage({
            role: 'assistant',
            content: `Error generating code: ${buildError instanceof Error ? buildError.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            id: `system-error-${Date.now()}`
          })
        }
      }
    } else {
      try {
        // Call the AI service
        const response = await AgentService.processChat(
          projectId.value,
          {
            prompt: prompt.value,
            model: store.selectedModelId,
            mode: 'chat',
            file: store.selectedFile
          }
        )
        
        // Add the real response message directly (dedupe against last assistant message)
        const normalize = (txt: string | undefined) => (txt || '').trim().replace(/\s+/g, ' ')
        const newContent = normalize(response.response)
        const lastAssistant = [...store.conversation].slice().reverse().find(m => m.role === 'assistant')
        const lastContent = normalize(lastAssistant?.content)
        if (!lastAssistant || newContent !== lastContent) {
          store.addMessage({
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString(),
            id: `assistant-response-${Date.now()}`
            // No code field to prevent displaying code in the UI
          })
        } else {
          console.info('Skipped duplicate assistant message (frontend dedupe)')
        }
      } catch (chatError) {
        throw chatError
      }
    }
    
    // Update balance exactly once after AI operation completes
    try {
      // Get fresh store to avoid stale references
      const balanceStore = useBalanceStore();
      
      // Wait a short delay to ensure backend transaction has completed
      setTimeout(() => {
        balanceStore.fetchBalance(false, true)
          .catch(err => console.warn('Error updating balance after AI operation:', err));
      }, 1000);
    } catch (err) {
      console.warn('Error setting up balance update:', err);
    }
    
    // Clear prompt after sending
    prompt.value = ''
  } catch (error) {
    console.error('Error processing prompt:', error)
  } finally {
    // Ensure processing flag is set to FALSE when everything is complete
    store.setProcessing(false)
  }
}

function handleExamplePrompt(exampleText: string) {
  prompt.value = exampleText
  handlePrompt()
}

async function handleModelSelect(modelId: string) {
  store.setSelectedModelId(modelId)
}

async function handleModeSwitch(mode: BuilderMode) {
  const previousMode = store.mode
  
  // Update the mode in the store
  store.setMode(mode)
  
  // If switching from chat to build and no file is selected
  if (previousMode === 'chat' && mode === 'build' && !store.selectedFile && store.files.length > 0) {
    // Auto-select the first file when switching to build mode
    store.selectFile(store.files[0])
  }
  
  // Only add system messages about mode changes if the new mode is chat mode
  // This prevents system messages from appearing in build mode
  if (mode === 'chat' && previousMode !== mode && store.conversation.length > 0) {
    // Add system message about mode change
    // Use a special ID format that can be detected in the ChatConversation component
    const modeChangeId = `system-mode-change-${Date.now()}`;
    
    store.conversation.push({
      role: 'system',
      content: `Switched to ${mode} mode${store.selectedFile ? ` for file: ${store.selectedFile.path}` : ''}`,
      timestamp: new Date().toISOString(),
      id: modeChangeId
    })
    
    // Brief delay to allow UI to settle after mode change
    await nextTick();
  }
}

function handleSelectApp(app: any) {
  selectedApp.value = app
}

function handleBackToList() {
  selectedApp.value = null
  selectedCategory.value = null
  store.setSelectedFile(null)
}

function handleCategoryChange(category: { key: string; label: string } | null) {
  selectedCategory.value = category
}

function handleBackToApps() {
  selectedApp.value = null
  selectedCategory.value = null
  store.setSelectedFile(null)
}

function handleBackToApp() {
  selectedCategory.value = null
  store.setSelectedFile(null)
}

function handleBackToCategory() {
  store.setSelectedFile(null)
}

function handleBackFromChat() {
  store.setSelectedFile(null)
}

// File picker methods
function toggleFilePicker() {
  isFilePickerOpen.value = !isFilePickerOpen.value
}

// Toggle file selection in context (multi-select)
function toggleFileContext(file: ProjectFile) {
  const index = selectedContextFiles.value.findIndex(f => f.path === file.path)
  if (index >= 0) {
    // Remove if already selected
    selectedContextFiles.value.splice(index, 1)
  } else {
    // Add if not selected
    selectedContextFiles.value.push(file)
  }
  
  // Update store with the primary selected file (first in list or null)
  if (selectedContextFiles.value.length > 0) {
    store.selectFile(selectedContextFiles.value[0])
  } else {
    store.setSelectedFile(null)
  }
}

// Check if a file is selected
function isFileSelected(filePath: string): boolean {
  return selectedContextFiles.value.some(f => f.path === filePath)
}

// Clear all file selections
function clearAllFileSelections() {
  selectedContextFiles.value = []
  store.setSelectedFile(null)
}

// Legacy single-select method (kept for compatibility)
function selectFileContext(file: ProjectFile) {
  store.selectFile(file)
  isFilePickerOpen.value = false
}

function clearFileSelection() {
  selectedContextFiles.value = []
  store.setSelectedFile(null)
  isFilePickerOpen.value = false
}

function handleCloseConversation() {
  store.clearConversation()
}

// Close file picker when clicking outside
function handleClickOutside(event: MouseEvent) {
  if (filePickerRef.value && !filePickerRef.value.contains(event.target as Node)) {
    isFilePickerOpen.value = false
  }
}

async function handleFileSelectFromDetail(file: ProjectFile) {
  // Set the selected file in store (for context in chat input)
  store.selectFile(file)
  
  // Also add to context files if not already there
  if (!selectedContextFiles.value.some(f => f.path === file.path)) {
    selectedContextFiles.value = [file]
  }
  
  // Force UI update
  await nextTick()
}

async function handleFileSelect(file: ProjectFile) {
  // Ensure selected file is set
  store.selectFile(file)
  showAppsInMain.value = false

  // Force UI update to reflect mode/selection changes
  await nextTick()
}

async function handleFileCreate(data: { name: string; type: string; content?: string }) {
  try {
    const created = await createFile({
      projectId: projectId.value,
      ...data
    })

    const createdPath = created?.path || ''
    const requestedPath = data?.name || ''
    const pathForMatch = createdPath || requestedPath
    const appMatch = pathForMatch.match(/src\/apps\/([^/]+)/i)

    // Determine file type for notification message
    const fileName = pathForMatch.split('/').pop() || 'file'
    const isView = data.name.includes('/views/')
    const isComponent = data.name.includes('/components/')
    const fileTypeLabel = isView ? 'View' : isComponent ? 'Component' : 'File'

    // If a view was created under an app, auto-register it in that app's router
    const viewInAppRegex = /(?:^|\/)(?:frontend\/vuejs\/)?src\/apps\/[^\/]+\/views\/[^\/]+\.vue$/i
    if (pathForMatch && viewInAppRegex.test(pathForMatch)) {
      try {
        await RouterUpdateService.addViewRoute(projectId.value, pathForMatch)
      } catch (e) {
        console.warn('Failed to auto-add route for created view:', pathForMatch, e)
      }
    }
    
    // Force refresh file list after creating a new file to ensure it appears in the explorer
    console.debug('File created, refreshing file list from backend...')
    await loadProjectFiles(true)

    // Stay in detail view if an app is selected
    if (appMatch?.[1] && !selectedApp.value) {
      // Find the app and show detail view
      const appFiles = store.files?.filter((f: any) => 
        (f.path || '').toLowerCase().includes(`/src/apps/${appMatch[1]}/`)
      ) || []
      if (appFiles.length > 0) {
        // Build app object
        const appKey = appMatch[1]
        const appName = appKey.charAt(0).toUpperCase() + appKey.slice(1)
        selectedApp.value = {
          key: appKey,
          name: appKey,
          displayName: appName,
          files: appFiles,
          icon: 'fas fa-cube',
          color: { bg: 'bg-violet-600/15', border: 'border-violet-400/30', text: 'text-violet-300' },
          hint: 'App files'
        }
      }
    }
    
    await nextTick()
    
    // Automatically commit the file creation
    VersionControlService.commitAfterFileOperation(
      projectId.value,
      created?.path || data.name,
      `Created ${created?.path || data.name}`
    )
    
    // Show success notification
    const { showNotification } = useNotification()
    showNotification({
      type: 'success',
      message: `${fileTypeLabel} "${fileName}" created successfully`,
      duration: 3000
    })
  } catch (error) {
    console.error('Error creating file:', error)
    
    // Show error notification
    const { showNotification } = useNotification()
    showNotification({
      type: 'error',
      message: `Failed to create file: ${error instanceof Error ? error.message : 'Unknown error'}`,
      duration: 5000
    })
  }
}

async function handleFileDelete(file: ProjectFile) {
  try {
    await FileService.deleteFile(projectId.value, file.path)
    
    // Force refresh file list after deleting a file to ensure it's removed from the explorer
    console.debug('File deleted, refreshing file list from backend...')
    await loadProjectFiles(true)
    
    // If the deleted file was selected, clear selection
    if (store.selectedFile && store.selectedFile.path === file.path) {
      store.setSelectedFile(null)
    }
    
    // Automatically commit the file deletion
    VersionControlService.commitAfterFileOperation(
      projectId.value,
      file.path,
      `Deleted ${file.path}`
    )
  } catch (error) {
    console.error('Error deleting file:', error)
  }
}

async function handlePreview() {
  try {
    if (!projectId.value) {
      return
    }

    const response = await PreviewService.generatePreview(projectId.value)
    
    if (response && response.previewUrl) {
      // Open the preview URL in a new tab
      window.open(response.previewUrl, '_blank')
    } else {
      // Show notification about preview failure
    }
  } catch (error) {
    console.error('Error starting preview server:', error)
  }
}

// Ensure default apps exist for every new project
async function ensureDefaultApps() {
  try {
    console.log('[BuilderWorkspace] Ensuring default apps for project:', projectId.value)
    
    // Call the backend API to ensure default apps exist
    const result = await BuilderCreationService.ensureDefaultApps(projectId.value)

    if (result.success) {
      console.log('[BuilderWorkspace] Default apps ensured successfully:', result.message)
      console.log('[BuilderWorkspace] Created apps:', result.created_apps || 'none')
      console.log('[BuilderWorkspace] Existing apps:', result.existing_frontend || 'none')
      
      // Reload project files to show any newly created default apps
      await loadProjectFiles(true)
      
      const { showNotification } = useNotification()
      if (result.created_apps && result.created_apps.length > 0) {
        showNotification({
          type: 'success',
          message: `Created ${result.created_apps.length} default app(s): ${result.created_apps.join(', ')}`,
          duration: 3000
        })
      }
    } else {
      console.error('[BuilderWorkspace] Failed to ensure default apps:', result.error)
      const { showNotification } = useNotification()
      showNotification({
        type: 'warning',
        message: 'Some default apps may not have been created. Check console for details.',
        duration: 4000
      })
    }
  } catch (e) {
    console.error('[BuilderWorkspace] Error ensuring default apps:', e)
    const { showNotification } = useNotification()
    showNotification({
      type: 'error',
      message: 'Error creating default apps. Please try refreshing.',
      duration: 5000
    })
  }
}

// Retry loading the project when user clicks retry button
async function retryProjectLoad() {
  // Clear any existing error state
  store.setError(null)
  
  try {
    // Retry loading the project
    await projectStore.fetchProject(projectId.value)
    
    // If successful, reload the workspace data
    await loadModels()
    // Force refresh files when retrying to ensure we get the latest state
    await loadProjectFiles(true)
    // Ensure default apps exist after retry load
    await ensureDefaultApps()
    // Refresh version history after retry
    await loadVersionHistory()
    
    // Set default model if needed
    if (!store.selectedModelId && store.availableModels && store.availableModels.length > 0) {
      const defaultModel = store.availableModels.find(m => m.id === 'claude-sonnet-4-20250514') 
        || store.availableModels[0];
      if (defaultModel) {
        store.setSelectedModelId(defaultModel.id);
      }
    }
    
    // Initialize mode if not set
    if (!store.mode) {
      store.setMode('chat');
    }
  } catch (error: any) {
    console.error('Error retrying project load:', error)
    store.setError(`Failed to load project: ${error.message || 'Unknown error'}`)
  }
}

// Helper function to load project files
async function loadProjectFiles(force = false) {
  try {
    // Always reload files when force is true, or when files haven't been loaded yet
    if (!force && store.files && store.files.length > 0) {
      console.debug('Using existing files from store, skipping API call')
      return store.files
    }
    
    console.debug('Loading project files from backend API...')
    const files = await FileService.getProjectFiles(projectId.value)
    if (Array.isArray(files)) {
      // Use the setFiles method to avoid type issues with $patch
      if (typeof store.setFiles === 'function') {
        // Cast the files to the expected type if needed
        store.setFiles(files as any)
        console.debug(`Loaded ${files.length} files from backend`)
      } else {
        console.error('setFiles method not available on store')
      }
      return files
    } else {
      console.error('Project files data is not an array:', files)
      return []
    }
  } catch (error) {
    console.error('Error loading project files:', error)
    return []
  }
}

// Lifecycle hooks
onMounted(async () => {
  // Get project ID from route params
  projectId.value = String(route.params.projectId)
  
  // IMPORTANT: Check if project is in deleted list BEFORE doing anything else
  // This prevents any API calls or initialization for deleted projects
  try {
    const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
    if (deletedProjects.includes(projectId.value)) {
      // Try to get project name from store if available
      let projectName = projectId.value;
      const existingProject = projectStore.getProjectById(projectId.value);
      if (existingProject?.name) {
        projectName = existingProject.name;
      }
      
      // Show notification and redirect immediately
      const { showNotification } = useNotification();
      showNotification({
        type: 'error',
        message: `Project "${projectName}" has been deleted.`,
        duration: 3000
      });
      
      // Immediate redirect without waiting
      router.replace({ name: 'builder-dashboard' });
      return; // Exit early to prevent any further initialization
    }
  } catch (e) {
    // Handle localStorage errors silently and continue
    console.warn('Error checking deleted projects list:', e)
  }
  
  try {
    // Get stores for easier access
    const paymentsStore = usePaymentStore();
    const authStore = useAuthStore();
    
    // Create a shared request cache to prevent duplicate calls
    const requestCache = new Map<string, Promise<any>>();
    
    // Helper function to deduplicate API calls
    const executeOnce = async (key: string, apiCall: () => Promise<any>) => {
      // Check if this API call is already in progress
      if (requestCache.has(key)) {
        console.debug(`Using existing API call promise for: ${key}`);
        return requestCache.get(key);
      }
      
      // Start a new API call and track it
      const promise = apiCall();
      requestCache.set(key, promise);
      
      try {
        // Execute the API call and return its result
        return await promise;
      } finally {
        // Remove the API call from tracking after completion
        setTimeout(() => {
          requestCache.delete(key);
        }, 100); // Short delay to prevent race conditions
      }
    };
    
    // First, verify authentication only once
    await executeOnce('verifyAuth', () => authStore.validateAuth());
    
    // Critical request - project must be loaded first and only once
    try {
      const project = await executeOnce('fetchProject', () => {
        // Directly return the API call result, don't wrap in another promise
        return projectStore.fetchProject(projectId.value);
      });
      
      // Set project ID in store only after project data is loaded
      if (project && typeof store.setProjectId === 'function') {
        store.setProjectId(projectId.value);
        
        // Now load models and files in sequence - files depend on project data
        // IMPORTANT: We DON'T use Promise.all here to prevent race conditions
        // between file fetching and the project data
        await executeOnce('loadModels', loadModels);
        // Force fresh file load on initial page load to always get latest files including initial home view
        await executeOnce('loadProjectFiles', () => loadProjectFiles(true));
        // Ensure default apps are present for new/empty projects
        await ensureDefaultApps()
        // Load version history for header dropdown
        await loadVersionHistory()
        
        // Only fetch balance once at startup, with no auto-refresh
        // Make sure it doesn't block the UI
        executeOnce('fetchBalance', () => paymentsStore.fetchBalance(false, false))
          .catch(err => console.error('Error fetching balance:', err));
        
        // Set default model if not already set
        if (!store.selectedModelId && store.availableModels && store.availableModels.length > 0) {
          const defaultModel = store.availableModels.find(m => m.id === 'claude-sonnet-4-20250514') 
            || store.availableModels[0];
          if (defaultModel) {
            store.setSelectedModelId(defaultModel.id);
          }
        }
        
        // Initialize mode if not set
        if (!store.mode) {
          store.setMode('chat');
        }
      } else {
        console.error('Failed to load project or set project ID');
        // Don't redirect - let the workspace show an error state
      }
    } catch (projectError: any) {
      console.error('Error loading project:', projectError);
      
      // Handle specific cases for missing projects
      if (projectError.message?.includes('Project not found') || 
          projectError.response?.status === 404) {
        console.log('Project not found - redirecting to dashboard');
        
        // Add project to deleted list if it resulted in 404
        try {
          const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
          if (!deletedProjects.includes(projectId.value)) {
            deletedProjects.push(projectId.value)
            localStorage.setItem('deletedProjects', JSON.stringify(deletedProjects))
            
            const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
            deletedProjectsTimestamp[projectId.value] = Date.now()
            localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
          }
        } catch (e) {
          console.warn('Failed to add project to deleted list:', e)
        }
        
        // Show a notification but redirect to dashboard to prevent further errors
        const { showNotification } = useNotification();
        showNotification({
          type: 'warning',
          message: 'Project not found. This project may have been deleted. Redirecting to dashboard...',
          duration: 4000
        });
        
        // Redirect to dashboard to prevent further 404 errors
        setTimeout(() => {
          router.push({ name: 'builder-dashboard' });
        }, 1500); // Give user time to read the notification
        
        // Set the workspace to an error state
        store.setError('Project not found. Redirecting to dashboard...');
      } else {
        // For other errors, stay on the page and show an error state
        console.error('Unexpected error during project initialization:', projectError);
        store.setError(`Error loading project: ${projectError.message || 'Unknown error'}`);
        
        // Show notification for other errors
        const { showNotification } = useNotification();
        showNotification({
          type: 'error',
          message: `Failed to load project: ${projectError.message || 'Unknown error'}`,
          duration: 5000
        });
      }
    }
  } catch (error) {
    console.error('Error initializing workspace:', error);
  }
  
  // Add click outside listener for file picker
  document.addEventListener('click', handleClickOutside)
})

// Watch for route parameter changes (e.g., if user navigates to different project)
watch(
  () => route.params.projectId,
  (newProjectId, oldProjectId) => {
    if (newProjectId && newProjectId !== oldProjectId) {
      console.debug('BuilderWorkspace: Project ID changed in route:', { oldProjectId, newProjectId })
      
      // Check if the new project is in the deleted list
      try {
        const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
        if (deletedProjects.includes(String(newProjectId))) {
          // Try to get project name from store if available
          let projectName = String(newProjectId);
          const existingProject = projectStore.getProjectById(String(newProjectId));
          if (existingProject?.name) {
            projectName = existingProject.name;
          }
          
          // Show notification and redirect immediately
          const { showNotification } = useNotification();
          showNotification({
            type: 'error',
            message: `Project "${projectName}" has been deleted.`,
            duration: 3000
          });
          
          // Immediate redirect without waiting
          router.replace({ name: 'builder-dashboard' });
          return;
        }
      } catch (e) {
        console.warn('Error checking deleted projects list during route change:', e)
      }
      
      // If not deleted, update the project ID and reload
      projectId.value = String(newProjectId)
      // Could add logic here to reload the project if needed
    }
  },
  { immediate: false } // Don't run immediately since onMounted handles the initial load
)

onBeforeUnmount(() => {
  // Clean up resources
  store.clearConversation()
  store.setSelectedFile(null)
  // Remove click outside listener
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Premium scrollbar - Matching Home Page */
:deep(::-webkit-scrollbar) {
  width: 6px;
}

:deep(::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.02);
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(139, 92, 246, 0.3);
  border-radius: 3px;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(139, 92, 246, 0.5);
}

/* Safe area padding for mobile */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>