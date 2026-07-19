<!--
  Workspace.vue - Project Editing Interface

  This component is responsible for:
  1. Loading an existing project's files and data
  2. Chatting with the Imagi agent, which edits project files directly
-->
<template>
  <div class="relative">
    <BuilderLayout
      storage-key="builderWorkspaceSidebarCollapsed"
      :navigation-items="navigationItems"
      :extra-wide="isManagerOpen"
    >
      <!-- Sidebar Content: Agent Manager + Active Instance Chat -->
      <template #sidebar-content="{ collapsed, toggleSidebar }">
        <div v-if="!collapsed" class="flex h-full">
          <AgentManagerPanel
            v-if="isManagerOpen || (isMobile && mobileView === 'manager')"
            class="w-56 shrink-0"
            :class="mobileView === 'manager' ? 'max-md:w-full' : 'max-md:hidden'"
            @collapse="toggleManager"
          />
          <BuilderSidebarChat
            class="flex-1 min-w-0"
            :class="mobileView === 'chat' ? 'max-md:w-full' : 'max-md:hidden'"
            :selected-app="null"
            :on-prompt-submit="handlePrompt"
            :on-model-select="handleModelSelect"
            :on-effort-select="handleEffortSelect"
            :on-example-prompt="handleExamplePrompt"
            :on-collapse-sidebar="() => collapseSidebar(toggleSidebar)"
            :is-collapsed="false"
            :is-manager-open="isManagerOpen"
            @toggle-manager="toggleManager"
          />
        </div>
      </template>

      <!-- Mobile-only view switcher, centered in the navbar: the logo sits in
           the top-left corner and the balance in the top-right, with this
           switcher (agent manager / instance / browser) centered between them.
           One view fills the screen at a time. -->
      <template #navbar-center="{ setSidebarCollapsed }">
        <div
          class="md:hidden flex items-center gap-0.5 rounded-lg border border-blue-100 dark:border-white/[0.08] bg-blue-50/70 dark:bg-white/[0.05] p-0.5"
          role="tablist"
          aria-label="Workspace view"
        >
          <button
            v-for="opt in mobileViewOptions"
            :key="opt.value"
            type="button"
            role="tab"
            :aria-selected="mobileView === opt.value"
            :aria-label="opt.label"
            :title="opt.label"
            @click="selectMobileView(opt.value, setSidebarCollapsed)"
            :class="[
              'flex items-center justify-center rounded-md px-2.5 py-1.5 text-xs font-medium transition-colors',
              mobileView === opt.value
                ? 'bg-white dark:bg-white/[0.12] text-blue-700 dark:text-white shadow-sm'
                : 'text-blue-950/55 dark:text-white/55 hover:text-blue-950 dark:hover:text-white'
            ]"
          >
            <i :class="[opt.icon, 'text-sm']"></i>
            <span class="sr-only">{{ opt.label }}</span>
          </button>
        </div>
      </template>

      <!-- Account balance display in navbar right -->
      <template #navbar-right>
        <div class="flex items-center gap-3">
          <AccountBalanceDisplay />
        </div>
      </template>

      <!-- Clean Main Content Area - fills the space below the navbar. Sized
           by the app-shell layout (h-full of the padded <main>) rather than a
           viewport calc, so it can never disagree with the shell and leave
           the page itself scrollable. -->
      <template #default="{ isSidebarCollapsed }">
        <div class="flex flex-col w-full h-full overflow-hidden bg-white dark:bg-[#0a0a0a] relative transition-colors duration-500">
          <!-- Enhanced Error State Display -->
          <WorkspaceError v-if="store.error" :error="store.error" @retry="retryProjectLoad" />

          <!-- Main Layout - embedded preview server. On mobile the browser pane
               is hidden (not unmounted, so the preview session stays warm)
               whenever the manager/chat overlay is open, so it can never peek
               out from behind that overlay. -->
          <div v-else class="flex-1 flex flex-col h-full min-h-0 overflow-hidden relative">
            <WorkspacePreview
              v-if="projectId"
              :project-id="projectId"
              class="flex-1 min-h-0"
              :class="isSidebarCollapsed ? '' : 'max-md:invisible'"
            />
          </div>
        </div>
      </template>
    </BuilderLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAgentStore } from '../stores/agentStore'
import { useBuilderMode } from '../composables/useBuilderMode'
import { useProjectStore } from '../stores/projectStore'
import { ProjectService } from '../services/projectService'
import { AgentService } from '../services/agentService'
import { FileService } from '../services/fileService'
import { BuilderCreationService } from '../services/builderCreationService'
import { VersionControlService } from '../services/versionControlService'
import { RouterUpdateService } from '../services/routerUpdateService'
import { useAuthStore } from '@/shared/stores/auth'
import { usePaymentStore } from '@/apps/payments/stores/payments'
import { useBalanceStore } from '@/shared/stores/balance'
import { useNotification } from '@/shared/composables/useNotification'
import { useWindowSize } from '@/shared/composables/useWindowSize'

// Builder Components
import { BuilderLayout } from '@/apps/imagi/build/layouts'
import { AccountBalanceDisplay } from '../components/molecules'

// Atomic Components
import {
  WorkspaceError,
  WorkspacePreview,
} from '../components/organisms/workspace'
import BuilderSidebarChat from '../components/organisms/sidebar/BuilderSidebarChat.vue'
import AgentManagerPanel from '../components/organisms/sidebar/AgentManagerPanel.vue'
// Set component name
defineOptions({ name: 'Workspace' })

// Types
import type { ProjectFile } from '../types/components'
import type { AIMessage } from '../types/index'
import type { ReasoningEffort } from '../types/services'
import { matchesSlug, toSlug } from '../utils/slug'

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
} = useBuilderMode()

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

// Agent manager open/closed (persisted)
const MANAGER_STORAGE_KEY = 'builderAgentManagerOpen'
const isManagerOpen = ref<boolean>(
  (typeof localStorage !== 'undefined' && localStorage.getItem(MANAGER_STORAGE_KEY)) !== 'false'
)
function toggleManager() {
  isManagerOpen.value = !isManagerOpen.value
  try {
    localStorage.setItem(MANAGER_STORAGE_KEY, String(isManagerOpen.value))
  } catch {}
}

// Mobile view switcher: on phones the manager, chat and preview each fill the
// screen one at a time instead of being crammed side by side.
const { isMobile } = useWindowSize()
type MobileView = 'manager' | 'chat' | 'browser'
// The sidebar's collapsed state is persisted (see storage-key on
// BuilderLayout). Start on the view that matches it, otherwise a reload after
// choosing the browser would highlight "chat" while showing the browser.
const mobileView = ref<MobileView>(
  (typeof localStorage !== 'undefined' &&
    localStorage.getItem('builderWorkspaceSidebarCollapsed') === 'true') ? 'browser' : 'chat'
)
const mobileViewOptions: Array<{ value: MobileView; label: string; icon: string }> = [
  { value: 'manager', label: 'Agents', icon: 'fas fa-layer-group' },
  { value: 'chat', label: 'Chat', icon: 'fas fa-comment-dots' },
  { value: 'browser', label: 'Preview', icon: 'fas fa-globe' },
]
function selectMobileView(view: MobileView, setSidebarCollapsed?: (collapsed: boolean) => void) {
  mobileView.value = view
  // The browser lives in the main content area, so it shows when the sidebar
  // (manager + chat) is collapsed off-screen; manager/chat show when it's open.
  setSidebarCollapsed?.(view === 'browser')
}

// Collapsing the sidebar from the chat header reveals the browser pane; keep
// the mobile view switcher pointed at it so the highlighted tab (and the
// browser pane's visibility) match what's on screen.
function collapseSidebar(toggleSidebar: () => void) {
  toggleSidebar()
  if (isMobile.value) mobileView.value = 'browser'
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
    const instance = store.activeInstance
    if (instance) store.setInstanceFile(instance.id, null)
  } catch (e) {
    console.error('Error handling version reset:', e)
  }
}

// Helper function to get just the filename
function getFileName(path: string): string {
  if (!path) return 'this file'
  const parts = path.split('/')
  return parts[parts.length - 1] ?? 'this file'
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

/** Turn an agent tool name into a status line the user can read. */
function describeAgentTool(name: string): string {
  if (name === 'update_plan') return 'Planning…'
  if (name === 'web_search' || name === 'web_search_call') return 'Searching the web…'
  if (['get_project_tree', 'list_project_files', 'glob_files', 'grep_files', 'read_file'].includes(name)) {
    return 'Reading project files…'
  }
  if (['edit_file', 'update_file', 'create_file', 'delete_file', 'create_directory', 'delete_directory'].includes(name)) {
    return 'Editing project files…'
  }
  return 'Working…'
}

async function handlePrompt(promptText: string) {
  if (!promptText.trim()) return

  const instance = store.activeInstance
  if (!instance) return
  if (!instance.selectedModelId) return
  if (!projectId.value) return

  const instanceId = instance.id
  const conversationIdBefore = instance.conversationId

  try {
    const timestamp = new Date().toISOString()

    // Mark pending transaction for fresh balance data
    const balanceStore = useBalanceStore()
    balanceStore.beginTransaction()

    store.setInstanceProcessing(instanceId, true)

    // Add the user message to this instance's conversation immediately
    store.addMessageToInstance(instanceId, {
      role: 'user',
      content: promptText,
      timestamp,
      id: `user-${Date.now()}`
    })

    // Auto-title from first user prompt (mirror backend behaviour for UI snappiness)
    if (!instance.title) {
      const firstLine = promptText.trim().split('\n')[0] || ''
      void store.renameInstance(instanceId, firstLine.slice(0, 80))
    }

    const isUserAuthenticated = await useAuthStore().validateAuth()
    if (!isUserAuthenticated) return

    // The assistant message is created empty and filled in as chunks arrive.
    const streamingMessageId = `assistant-response-${Date.now()}`
    let streamedText = ''
    let messageStarted = false

    try {
      store.setInstanceStatus(instanceId, 'Thinking…')
      const response = await AgentService.streamAgent(
        projectId.value,
        {
          prompt: promptText,
          model: instance.selectedModelId,
          reasoningEffort: instance.selectedEffort,
          file: instance.selectedFile,
          conversationId: conversationIdBefore ?? undefined
        },
        {
          onStart: (conversationId) => {
            if (conversationId && !instance.conversationId) {
              store.updateInstanceConversationId(instanceId, conversationId)
            }
          },
          onDelta: (text) => {
            // Defer creating the message until there is something to show, so
            // a tools-only turn does not leave an empty bubble behind.
            if (!messageStarted) {
              messageStarted = true
              store.addMessageToInstance(instanceId, {
                role: 'assistant',
                content: '',
                timestamp: new Date().toISOString(),
                id: streamingMessageId
              })
            }
            // The reply is streaming; the status line would just sit under it.
            store.setInstanceStatus(instanceId, '')
            streamedText += text
            store.setMessageContent(instanceId, streamingMessageId, streamedText)
          },
          onToolCall: (name) => {
            store.setInstanceStatus(instanceId, describeAgentTool(name))
          },
        }
      )

      if ((response as any).conversation_id && !instance.conversationId) {
        store.updateInstanceConversationId(instanceId, (response as any).conversation_id)
      }

      // Reconcile with the run's authoritative final text: deltas can miss
      // content the model emitted without streaming it.
      if (response.response && response.response !== streamedText) {
        if (messageStarted) {
          store.setMessageContent(instanceId, streamingMessageId, response.response)
        } else {
          store.addMessageToInstance(instanceId, {
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString(),
            id: streamingMessageId
          })
        }
      }

      if (response.files_changed && response.files_changed.length > 0) {
        for (const changedPath of response.files_changed) {
          try {
            const files = await FileService.getProjectFiles(projectId.value)
            store.setFiles(files)
          } catch (refreshError) {
            console.warn('Error refreshing files after agent edit:', refreshError)
          }
          createCommitFromPrompt(changedPath, promptText)
        }
      }
    } catch (agentError) {
      console.error('Error processing agent request:', agentError)
      store.addMessageToInstance(instanceId, {
        role: 'assistant',
        content: `Error: ${agentError instanceof Error ? agentError.message : 'Unknown error'}`,
        timestamp: new Date().toISOString(),
        id: `system-error-${Date.now()}`
      })
    }

    try {
      setTimeout(() => {
        useBalanceStore().fetchBalance(false, true)
          .catch(err => console.warn('Error updating balance after AI operation:', err))
      }, 1000)
    } catch (err) {
      console.warn('Error setting up balance update:', err)
    }
  } catch (error) {
    console.error('Error processing prompt:', error)
    // Failures outside the agent call (store errors, setup bugs) must still
    // surface in the chat — a console-only error reads as "nothing happened".
    store.addMessageToInstance(instanceId, {
      role: 'assistant',
      content: `Error: ${error instanceof Error ? error.message : 'Something went wrong processing your request.'}`,
      timestamp: new Date().toISOString(),
      id: `system-error-${Date.now()}`
    })
  } finally {
    store.setInstanceProcessing(instanceId, false)
  }
}

function handleExamplePrompt(exampleText: string) {
  handlePrompt(exampleText)
}

async function handleModelSelect(modelId: string) {
  const instance = store.activeInstance
  if (!instance) return
  store.setInstanceModel(instance.id, modelId)
}

async function handleEffortSelect(effort: ReasoningEffort) {
  const instance = store.activeInstance
  if (!instance) return
  store.setInstanceEffort(instance.id, effort)
}

async function handleFileSelect(file: ProjectFile) {
  // Ensure selected file is set on the active instance
  const instance = store.activeInstance
  if (instance) store.setInstanceFile(instance.id, file)
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
    const viewInAppRegex = /(?:^|\/)(?:frontend\/vuejs\/)?src\/apps\/[^/]+\/views\/[^/]+\.vue$/i
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
    
    // If the deleted file was selected in any instance, clear that selection
    for (const inst of store.instances) {
      if (inst.selectedFile && inst.selectedFile.path === file.path) {
        store.setInstanceFile(inst.id, null)
      }
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

// Ensure default apps exist for every new project
async function ensureDefaultApps() {
  try {
    // Call the backend API to ensure default apps exist
    const result = await BuilderCreationService.ensureDefaultApps(projectId.value)

    if (result.success) {
      
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
      console.error('[Workspace] Failed to ensure default apps:', result.error)
      const { showNotification } = useNotification()
      showNotification({
        type: 'warning',
        message: 'Some default apps may not have been created. Check console for details.',
        duration: 4000
      })
    }
  } catch (e) {
    console.error('[Workspace] Error ensuring default apps:', e)
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
    
    await store.loadInstances(projectId.value)

    const active = store.activeInstance
    if (active && !active.selectedModelId && store.availableModels && store.availableModels.length > 0) {
      const defaultModel = store.availableModels.find(m => m.id === 'gpt-5.6-sol')
        || store.availableModels[0];
      if (defaultModel) {
        store.setInstanceModel(active.id, defaultModel.id)
      }
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
  // Get project name from route params (URL slug)
  const projectNameSlug = String(route.params.projectName)
  
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
    
    // Load projects list to find the project by slug
    await executeOnce('fetchProjects', () => projectStore.fetchProjects());
    
    // Find the project by slug
    const foundProject = projectStore.getProjectBySlug(projectNameSlug);
    
    if (!foundProject) {
      console.error('Project not found for slug:', projectNameSlug);
      const { showNotification } = useNotification();
      showNotification({
        type: 'error',
        message: `Project "${projectNameSlug}" not found.`,
        duration: 3000
      });
      router.replace({ name: 'projects' });
      return;
    }
    
    // Set the project ID from the found project
    projectId.value = String(foundProject.id);

    // Gate: the workspace must not open while the initial AI build is still
    // running, or the user would land in a half-built project. Check the
    // authoritative status and, if it's still generating, bounce back to the
    // project hub where the "Building your app" state is shown. This is the
    // backstop for direct URLs / refreshes; the hub's Build card also blocks
    // navigation while building.
    try {
      const status = await ProjectService.getProjectStatus(projectId.value)
      if (status.generation_status === 'generating') {
        const { showNotification } = useNotification()
        showNotification({
          type: 'info',
          message: `Imagi is still building "${foundProject.name}". We'll open the workspace as soon as it's ready.`,
          duration: 4000
        })
        router.replace({ name: 'project-hub', params: { projectName: projectNameSlug } })
        return
      }
    } catch (e) {
      // If the status check fails, don't block entry — fall through and load
      // the workspace as normal rather than trapping the user.
      console.warn('Could not verify initial build status; opening workspace anyway:', e)
    }

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

        // Load agent instances for this project (creates a starter instance if none)
        await executeOnce('loadInstances', () => store.loadInstances(projectId.value))

        // Only fetch balance once at startup, with no auto-refresh
        executeOnce('fetchBalance', () => paymentsStore.fetchBalance(false, false))
          .catch(err => console.error('Error fetching balance:', err));

        // Ensure active instance has a model selected
        const active = store.activeInstance
        if (active && !active.selectedModelId && store.availableModels && store.availableModels.length > 0) {
          const defaultModel = store.availableModels.find(m => m.id === 'gpt-5.6-sol')
            || store.availableModels[0];
          if (defaultModel) {
            store.setInstanceModel(active.id, defaultModel.id)
          }
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

        // Show a notification but redirect to dashboard to prevent further errors
        const { showNotification } = useNotification();
        showNotification({
          type: 'warning',
          message: 'Project not found. This project may have been deleted. Redirecting to dashboard...',
          duration: 4000
        });
        
        // Redirect to dashboard to prevent further 404 errors
        setTimeout(() => {
          router.push({ name: 'projects' });
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
  () => route.params.projectName,
  async (newProjectName, oldProjectName) => {
    if (newProjectName && newProjectName !== oldProjectName) {
      console.debug('Workspace: Project name changed in route:', { oldProjectName, newProjectName })
      
      // Find the new project by slug
      const foundProject = projectStore.getProjectBySlug(String(newProjectName));
      
      if (!foundProject) {
        // Try to load projects and search again
        await projectStore.fetchProjects();
        const retryProject = projectStore.getProjectBySlug(String(newProjectName));
        
        if (!retryProject) {
          const { showNotification } = useNotification();
          showNotification({
            type: 'error',
            message: `Project "${newProjectName}" not found.`,
            duration: 3000
          });
          router.replace({ name: 'projects' });
          return;
        }
        
        projectId.value = String(retryProject.id);
        return;
      }
      
      const newProjectId = String(foundProject.id);

      // Update the project ID and reload
      projectId.value = newProjectId
      // Could add logic here to reload the project if needed
    }
  },
  { immediate: false } // Don't run immediately since onMounted handles the initial load
)

onBeforeUnmount(() => {
  // Conversations are persisted server-side; no local cleanup needed.
  store.setError(null)
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

/* Refined minimal scrollbar - Matching Homepage */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}

/* Safe area padding for mobile */
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>