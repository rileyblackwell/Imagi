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
      <!-- Sidebar Content -->
      <template #sidebar-content="{ collapsed }">
        <BuilderSidebar
          :current-project="currentProject"
          :selected-file="store.selectedFile || null"
          :files="store.files || []"
          :file-types="fileTypes"
          :is-loading="store.isProcessing || false"
          :current-editor-mode="currentEditorMode"
          :is-collapsed="collapsed"
          :project-id="projectId || ''"
          @select-file="handleFileSelect"
          @create-file="handleFileCreate"
          @delete-file="handleFileDelete"
          @preview="handlePreview"
        />
      </template>

      <!-- Modern Dark-themed Main Content Area -->
      <div class="flex flex-col h-screen max-h-screen w-full overflow-hidden bg-dark-950 relative">
        <!-- Enhanced sophisticated dark background with enhanced effects matching About page -->
        <div class="absolute inset-0 pointer-events-none overflow-hidden">
          <!-- Enhanced Pattern Overlay -->
          <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
          <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
          <div class="absolute inset-0 bg-gradient-to-br from-dark-950/10 via-dark-900 to-violet-950/10"></div>
          
          <!-- Enhanced Glowing Orbs Animation -->
          <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
          <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-violet-600/5 blur-[120px] animate-float-delay"></div>
          
          <!-- Animated Lines and Particles -->
          <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
          <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
        </div>
        
        <!-- Subtle top border for definition -->
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent"></div>

        <!-- Enhanced Error State Display -->
        <div v-if="store.error" class="flex-1 flex flex-col h-full overflow-hidden relative z-10">
          <div class="flex flex-col items-center justify-center h-full p-12 text-center">
            <!-- Modern Error Container -->
            <div class="relative group max-w-xl w-full transform transition-all duration-300 hover:-translate-y-1">
              <!-- Enhanced glassmorphism Error Card -->
              <div class="absolute -inset-0.5 rounded-2xl opacity-70 bg-gradient-to-r from-red-500/50 to-rose-500/50 blur-md"></div>
              <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/95 via-dark-900/90 to-dark-800/95 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                <!-- Sleek gradient header -->
                <div class="h-1 w-full bg-gradient-to-r from-red-400 via-rose-400 to-red-400 opacity-80"></div>
                
                <!-- Subtle background effects -->
                <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-red-400/4 to-rose-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
                
                <div class="relative z-10 p-8">
                  <!-- Modern pill badge -->
                  <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-red-500/15 to-rose-500/15 border border-red-400/20 rounded-full mb-6 backdrop-blur-sm mx-auto">
                    <div class="w-1.5 h-1.5 bg-red-400 rounded-full mr-2 animate-pulse"></div>
                    <span class="text-red-300 font-medium text-xs tracking-wide uppercase">Workspace Error</span>
                  </div>
                  
                  <!-- Error Icon -->
                  <div class="w-16 h-16 bg-gradient-to-br from-red-500/20 to-rose-500/20 border border-red-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                    <i class="fas fa-exclamation-triangle text-2xl text-red-400"></i>
                  </div>
                  
                  <!-- Error Content -->
                  <h2 class="text-2xl font-semibold text-white mb-4">Something went wrong</h2>
                  <p class="text-gray-300 mb-8 leading-relaxed">{{ store.error }}</p>
                  
                  <!-- Action Buttons -->
                  <div class="flex flex-col sm:flex-row gap-4 justify-center">
                    <router-link
                      to="/products/oasis/builder/dashboard"
                      class="inline-flex items-center justify-center px-6 py-3 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-200 transform hover:-translate-y-1"
                    >
                      <i class="fas fa-arrow-left mr-2"></i>
                      Go to Dashboard
                    </router-link>
                    <button
                      @click="retryProjectLoad"
                      class="inline-flex items-center justify-center px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-red-400/30 text-gray-300 hover:text-white font-medium rounded-xl transition-all duration-200"
                    >
                      <i class="fas fa-sync-alt mr-2"></i>
                      Retry
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Enhanced ChatGPT-like Interface -->
        <div v-else class="flex-1 flex flex-col h-full min-h-0 overflow-hidden relative z-10">
          <!-- Main Content: Show Apps section first; switch to chat after submit -->
          <div class="flex-1 flex flex-col h-full min-h-0 relative">
            <!-- Apps Section (moved from sidebar) with chat input kept visible below -->
            <div v-if="showAppsInMain" class="flex-1 min-h-0 p-4 flex flex-col">
              <div class="flex-1 min-h-0 relative rounded-2xl border overflow-hidden bg-dark-800/60 backdrop-blur-md border-dark-700/60">
                <div class="h-0.5 w-full bg-gradient-to-r from-indigo-500/30 via-violet-500/30 to-indigo-500/30 opacity-70"></div>
                <div class="px-4 py-3 flex items-center justify-between">
                  <span class="inline-flex items-center gap-2">
                    <span class="w-7 h-7 rounded-md flex items-center justify-center border bg-gradient-to-br from-primary-500/15 to-violet-500/15 border-primary-500/30 text-primary-300">
                      <i class="fas fa-th-large"></i>
                    </span>
                    <span class="text-sm font-semibold uppercase tracking-wider bg-gradient-to-r from-indigo-300 to-violet-300 bg-clip-text text-transparent">Apps</span>
                  </span>
                  <span class="text-[11px] px-2 py-0.5 rounded-full border bg-dark-800/60 border-dark-700/50 text-gray-300">{{ appsCount }} app{{ appsCount !== 1 ? 's' : '' }}</span>
                </div>
                <div class="p-2 h-[calc(100%-44px)]">
                  <FileExplorer
                    :files="store.files || []"
                    :selected-file="store.selectedFile || null"
                    :file-types="fileTypes"
                    :show-new-form="false"
                    :project-id="projectId || ''"
                    @select-file="handleFileSelect"
                    @create-file="handleFileCreate"
                    @delete-file="handleFileDelete"
                  />
                </div>
              </div>

              <!-- Compact chat input section fixed below Apps area -->
              <div class="mt-4">
                <WorkspaceChat
                  :messages="ensureValidMessages(store.conversation || [])"
                  :is-processing="store.isProcessing"
                  :mode="store.mode || 'chat'"
                  :selected-file="store.selectedFile"
                  :selected-model-id="store.selectedModelId"
                  :available-models="store.availableModels || []"
                  :prompt-placeholder="promptPlaceholder"
                  :show-examples="false"
                  :prompt-examples="promptExamplesComputed"
                  v-model="prompt"
                  :compact="true"
                  :show-conversation="false"
                  @update:model-id="handleModelSelect"
                  @update:mode="handleModeSwitch"
                  @submit="handlePrompt"
                  @use-example="handleExamplePrompt"
                />
              </div>
            </div>

            <!-- Chat Component -->
            <div v-else class="flex-1 relative min-h-0">
              <WorkspaceChat
                :messages="ensureValidMessages(store.conversation || [])"
                :is-processing="store.isProcessing"
                :mode="store.mode || 'chat'"
                :selected-file="store.selectedFile"
                :selected-model-id="store.selectedModelId"
                :available-models="store.availableModels || []"
                :prompt-placeholder="promptPlaceholder"
                :show-examples="false"
                :prompt-examples="promptExamplesComputed"
                v-model="prompt"
                @update:model-id="handleModelSelect"
                @update:mode="handleModeSwitch"
                @submit="handlePrompt"
                @use-example="handleExamplePrompt"
                class="h-full w-full"
                style="height: 100%; overflow: hidden; display: flex; flex-direction: column;"
              />
            </div>
          </div>
        </div>
      </div>
    </BuilderLayout>
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
import { VersionControlService } from '../services/versionControlService'
import { useAuthStore } from '@/shared/stores/auth'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useBalanceStore } from '@/shared/stores/balance'
import { useNotification } from '@/shared/composables/useNotification'

// Builder Components
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import BuilderSidebar from '../components/organisms/sidebar/BuilderSidebar.vue'
import { AccountBalanceDisplay } from '../components/molecules'

// Atomic Components
import { WorkspaceChat } from '../components/organisms/workspace'
import FileExplorer from '../components/molecules/sidebar/FileExplorer.vue'
// Set component name
defineOptions({ name: 'BuilderWorkspace' })

// Types
import type { ProjectFile, EditorMode, BuilderMode } from '../types/components'
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

// Local state
const currentEditorMode = ref<EditorMode>('split')
const prompt = ref('')
const showAppsInMain = ref(true)

// Navigation items for sidebar
const navigationItems: any[] = [] // Empty array to remove sidebar navigation buttons

// Computed properties
const currentProject = computed(() => {
  return projectStore.currentProject || null
})

// Apps count (unique apps derived from files) used in the Apps header
const appsCount = computed(() => {
  const apps = new Set<string>()
  ;(store.files || []).forEach((file: any) => {
    const path = String(file.path || '').toLowerCase().replace(/\\/g, '/')
    const match = path.match(/\/src\/apps\/([^\/]+)\//)
    if (match) apps.add(match[1])
  })
  return apps.size
})

const promptExamplesComputed = computed(() => {
  return [] // Return empty array for examples
})

const promptPlaceholder = computed(() => {
  if (store.mode === 'chat') {
    return store.selectedFile 
      ? `Ask me anything about ${store.selectedFile.path} or your project...`
      : 'Ask me anything about your project, get coding help, or discuss architecture...'
  } else {
    return store.selectedFile
      ? `Describe the changes you want to make to ${getFileName(store.selectedFile.path)}...`
      : 'Select a file from the sidebar to start building...'
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

async function handlePrompt(eventData?: { timestamp: string }) {
  if (!prompt.value.trim()) return
  
  try {
    // Switch main area from Apps to Chat upon first submission
    if (showAppsInMain.value) {
      showAppsInMain.value = false
    }
    if (!store.selectedModelId) {
      return
    }
    
    const timestamp = eventData?.timestamp || new Date().toISOString()
    
    // Get payments store for updating balance
    const paymentsStore = usePaymentStore()
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

async function handleFileSelect(file: ProjectFile) {
  if (store.selectedFile?.path !== file.path) {
    // Remove system messages about file changes completely
    // No longer add file switch notifications to the conversation
    
    // Determine file type before selecting the file
    const fileExtension = file.path.split('.').pop()?.toLowerCase() || '';
    const isCSS = fileExtension === 'css' || file.type === 'css';
    const isHTML = fileExtension === 'html' || file.type === 'html';
    
    // Use the improved selectFile method to maintain chat context
    store.selectFile(file)
    
    // Update the mode indicator UI by forcing a re-render
    // This is needed because the selectedFile reference might not change
    // if the file content is the same, but we still want the UI to update
    await nextTick()
  }
}

async function handleFileCreate(data: { name: string; type: string; content?: string }) {
  try {
    await createFile({
      projectId: projectId.value,
      ...data
    })
    
    // Force refresh file list after creating a new file to ensure it appears in the explorer
    console.debug('File created, refreshing file list from backend...')
    await loadProjectFiles(true)
    
    // Automatically commit the file creation
    VersionControlService.commitAfterFileOperation(
      projectId.value,
      data.name,
      `Created ${data.name}`
    )
  } catch (error) {
    console.error('Error creating file:', error)
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

/* Ultra-premium background effects */
.bg-grid-pattern {
  background-image: linear-gradient(to right, theme('colors.dark.800') 1px, transparent 1px),
                    linear-gradient(to bottom, theme('colors.dark.800') 1px, transparent 1px);
  background-size: 20px 20px;
}

/* Sophisticated orchestrated floating animations */
@keyframes float-orchestrated-1 {
  0%, 100% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); }
  25% { transform: translateY(-40px) translateX(25px) rotate(0.8deg) scale(1.02); }
  50% { transform: translateY(-20px) translateX(35px) rotate(-0.3deg) scale(1.05); }
  75% { transform: translateY(-35px) translateX(-10px) rotate(0.5deg) scale(1.01); }
}

@keyframes float-orchestrated-2 {
  0%, 100% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); }
  30% { transform: translateY(-30px) translateX(-20px) rotate(-0.6deg) scale(1.03); }
  60% { transform: translateY(10px) translateX(30px) rotate(0.4deg) scale(1.04); }
  90% { transform: translateY(-15px) translateX(-5px) rotate(-0.2deg) scale(1.01); }
}

@keyframes float-orchestrated-3 {
  0%, 100% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); }
  40% { transform: translateY(25px) translateX(-25px) rotate(0.7deg) scale(1.06); }
  70% { transform: translateY(-20px) translateX(15px) rotate(-0.4deg) scale(1.02); }
}

@keyframes float-orchestrated-4 {
  0%, 100% { transform: translateY(0) translateX(0) rotate(0deg) scale(1); }
  35% { transform: translateY(-25px) translateX(20px) rotate(-0.5deg) scale(1.04); }
  65% { transform: translateY(15px) translateX(-30px) rotate(0.3deg) scale(1.07); }
}

.animate-float-orchestrated-1 {
  animation: float-orchestrated-1 28s ease-in-out infinite;
}

.animate-float-orchestrated-2 {
  animation: float-orchestrated-2 35s ease-in-out infinite reverse;
}

.animate-float-orchestrated-3 {
  animation: float-orchestrated-3 32s ease-in-out infinite;
}

.animate-float-orchestrated-4 {
  animation: float-orchestrated-4 40s ease-in-out infinite reverse;
}

/* Sophisticated pulse animations for decorative elements */
@keyframes pulse-sophisticated {
  0%, 100% { 
    opacity: 0.8; 
    transform: scaleX(1); 
  }
  25% { 
    opacity: 0.4; 
    transform: scaleX(1.02); 
  }
  50% { 
    opacity: 0.6; 
    transform: scaleX(0.98); 
  }
  75% { 
    opacity: 0.3; 
    transform: scaleX(1.01); 
  }
}

.animate-pulse-sophisticated {
  animation: pulse-sophisticated 4s ease-in-out infinite;
}

/* Sophisticated delay system */
.delay-1200 {
  animation-delay: 1200ms;
}

.delay-2400 {
  animation-delay: 2400ms;
}

.delay-3600 {
  animation-delay: 3600ms;
}

/* Safe area padding for mobile */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}

/* Ensure proper z-index layering */
.relative {
  position: relative;
}

/* Enhanced animations matching About page */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
}

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

.delay-700 {
  animation-delay: 700ms;
}

/* Legacy animations for compatibility */
@keyframes float-slow {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-20px) translateX(10px); }
}

@keyframes float-slow-reverse {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(20px) translateX(-10px); }
}

.animate-float-slow {
  animation: float-slow 20s ease-in-out infinite;
}

.animate-float-slow-reverse {
  animation: float-slow-reverse 25s ease-in-out infinite;
}
</style>