<template>
  <DashboardLayout>
    <div class="builder-workspace">
      <!-- Sidebar -->
      <aside class="builder-sidebar" :class="{ 'collapsed': isSidebarCollapsed }">
        <button 
          class="collapse-btn" 
          @click="toggleSidebar"
          :title="isSidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        >
          <i class="fas" :class="isSidebarCollapsed ? 'fa-chevron-right' : 'fa-chevron-left'"></i>
        </button>

        <div class="sidebar-controls">
          <!-- Model Selection -->
          <div class="select-wrapper">
            <label for="model-select">Model</label>
            <select 
              id="model-select" 
              v-model="selectedModel"
              class="styled-select"
            >
              <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
            </select>
          </div>

          <!-- Mode Selection -->
          <div class="select-wrapper">
            <label for="mode-select">Mode</label>
            <select 
              id="mode-select" 
              v-model="mode"
              class="styled-select"
            >
              <option value="chat">Chat Mode</option>
              <option value="build">Build Mode</option>
            </select>
          </div>

          <!-- File Selection -->
          <div class="select-wrapper">
            <label for="file-select">File</label>
            <select 
              id="file-select" 
              v-model="selectedFile"
              class="styled-select"
            >
              <option value="base.html">base.html</option>
              <option value="index.html">index.html</option>
              <option value="about.html">about.html</option>
              <option value="contact.html">contact.html</option>
              <option value="styles.css">styles.css</option>
              <option value="custom">+ Add New File</option>
            </select>

            <!-- Custom File Input -->
            <div v-if="selectedFile === 'custom'" class="custom-page-input">
              <div class="input-group">
                <input 
                  type="text" 
                  v-model="newFileName"
                  placeholder="Enter file name (e.g., gallery.html)"
                  class="styled-input"
                >
                <button 
                  @click="addNewFile"
                  class="sidebar-btn"
                  :disabled="!newFileName"
                >
                  <i class="fas fa-plus"></i>
                  <span>Add</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="sidebar-buttons">
            <button 
              class="sidebar-btn"
              @click="undoLastAction"
              :disabled="!canUndo"
            >
              <i class="fas fa-undo"></i>
              <span>Undo</span>
            </button>

            <button 
              class="sidebar-btn"
              @click="previewProject"
              :disabled="isGenerating"
            >
              <i class="fas fa-eye"></i>
              <span>Preview</span>
            </button>

            <!-- File Upload -->
            <div class="file-upload-wrapper">
              <label for="file-upload" class="file-upload-label">
                <i class="fas fa-upload"></i>
                <span>Upload File</span>
              </label>
              <input 
                type="file" 
                id="file-upload"
                @change="handleFileUpload"
                accept=".html,.css,.js"
                class="file-upload-input"
              >
              <div class="file-name-display">{{ uploadedFileName }}</div>
            </div>
          </div>
        </div>

        <!-- Chat History -->
        <div class="chat-history">
          <div 
            v-for="conversation in conversations"
            :key="conversation.id"
            class="chat-history-item"
            :class="{ active: currentConversation?.id === conversation.id }"
            @click="loadConversation(conversation)"
          >
            <i class="fas fa-comment"></i>
            <span class="chat-title">{{ conversation.title }}</span>
          </div>
        </div>

        <!-- Sidebar Footer -->
        <div class="sidebar-footer">
          <router-link 
            to="/builder"
            class="sidebar-link"
          >
            <i class="fas fa-th-large"></i>
            <span>Projects Dashboard</span>
          </router-link>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content" :class="{ 'expanded': isSidebarCollapsed }">
        <div class="chat-container">
          <!-- Response Window -->
          <div id="response-window" class="response-window" ref="responseWindow">
            <!-- Welcome Screen -->
            <div v-if="showWelcome" class="welcome-screen">
              <div class="welcome-icon">
                <i class="fas fa-magic"></i>
              </div>
              <h1>Welcome to Imagi Oasis</h1>
              <p>Transform your ideas into stunning web apps using natural language. Just describe what you want to build, and I'll help you create it.</p>
              
              <div class="welcome-examples">
                <h2>Example prompts to get started:</h2>
                <div class="example-prompts">
                  <button 
                    v-for="(prompt, index) in examplePrompts"
                    :key="index"
                    class="example-prompt"
                    @click="useExamplePrompt(prompt)"
                  >
                    {{ prompt }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Chat Messages -->
            <template v-else>
              <div 
                v-for="(message, index) in messages"
                :key="index"
                class="chat-message"
                :class="message.role"
              >
                <div class="role">{{ message.role === 'user' ? 'You' : 'Assistant' }}</div>
                <div class="content" v-html="formatMessage(message.content)"></div>
              </div>
            </template>
          </div>

          <!-- Chat Input -->
          <div class="chat-input">
            <form @submit.prevent="sendMessage" class="input-container">
              <div class="input-wrapper">
                <textarea
                  id="user-input"
                  v-model="userInput"
                  :placeholder="inputPlaceholder"
                  rows="1"
                  @input="autoResizeInput"
                  @keydown.enter.prevent="handleEnterKey"
                  ref="inputField"
                ></textarea>
                <button 
                  type="submit"
                  id="submit-btn"
                  :disabled="isGenerating || !userInput.trim()"
                  title="Send message"
                >
                  <i class="fas" :class="isGenerating ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
                </button>
              </div>
              <div class="bottom-text">
                Imagi can make mistakes. Consider checking important information.
              </div>
            </form>
          </div>
        </div>
      </main>
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DashboardLayout from '@/shared/layouts/DashboardLayout.vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import axios from 'axios'

export default {
  name: 'BuilderWorkspace',
  components: {
    DashboardLayout
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const projectId = route.params.projectId

    // State
    const isSidebarCollapsed = ref(false)
    const selectedModel = ref('claude-3-5-sonnet-20241022')
    const mode = ref('chat')
    const selectedFile = ref('index.html')
    const newFileName = ref('')
    const userInput = ref('')
    const messages = ref([])
    const isGenerating = ref(false)
    const showWelcome = ref(true)
    const uploadedFileName = ref('')
    const conversations = ref([])
    const currentConversation = ref(null)
    const responseWindow = ref(null)
    const inputField = ref(null)
    const projectFiles = ref([])
    const hasInsufficientCredits = ref(false)
    const requiredCredits = ref(0)

    const examplePrompts = [
      'Create a modern landing page with a hero section and features grid',
      'Add a contact form with name, email, and message fields',
      'Style the navigation bar to be sticky and transparent'
    ]

    const inputPlaceholder = computed(() => {
      return mode.value === 'chat' 
        ? 'Chat about your website ideas...'
        : 'Describe what you want to build or modify in this file...'
    })

    const canUndo = computed(() => {
      return messages.value.filter(m => m.role === 'assistant').length > 1
    })

    // Methods
    const toggleSidebar = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value
      localStorage.setItem('builderSidebarCollapsed', isSidebarCollapsed.value)
    }

    const autoResizeInput = () => {
      const el = inputField.value
      el.style.height = 'auto'
      el.style.height = el.scrollHeight + 'px'
    }

    const handleEnterKey = (e) => {
      if (!e.shiftKey) {
        sendMessage()
      }
    }

    const formatMessage = (content) => {
      // Sanitize and convert markdown to HTML
      return DOMPurify.sanitize(marked(content))
    }

    const scrollToBottom = async () => {
      await nextTick()
      if (responseWindow.value) {
        responseWindow.value.scrollTop = responseWindow.value.scrollHeight
      }
    }

    const loadProjectFiles = async () => {
      try {
        const response = await axios.get(`/api/builder/project-files/${projectId}/`)
        projectFiles.value = response.data.files
        
        // Update file selector options
        if (projectFiles.value.length > 0) {
          selectedFile.value = projectFiles.value[0]
        }
      } catch (error) {
        console.error('Error loading project files:', error)
      }
    }

    const loadConversationHistory = async () => {
      try {
        const response = await axios.get(`/api/builder/conversation-history/${projectId}/`)
        conversations.value = response.data.conversations
        
        // Set current conversation if exists
        if (conversations.value.length > 0) {
          currentConversation.value = conversations.value[0]
          messages.value = currentConversation.value.messages
          showWelcome.value = false
        }
      } catch (error) {
        console.error('Error loading conversation history:', error)
      }
    }

    const handleInsufficientCredits = (required) => {
      hasInsufficientCredits.value = true
      requiredCredits.value = required
      router.push({
        name: 'payments',
        query: { 
          redirect: route.fullPath,
          required: required
        }
      })
    }

    const sendMessage = async () => {
      if (!userInput.value.trim() || isGenerating.value) return

      const message = userInput.value
      userInput.value = ''
      showWelcome.value = false
      isGenerating.value = true

      // Add user message
      messages.value.push({
        role: 'user',
        content: message
      })

      await scrollToBottom()

      try {
        const endpoint = mode.value === 'chat' ? '/api/builder/chat/' : '/api/builder/process-input/'
        const payload = {
          user_input: message,
          model: selectedModel.value,
          file: selectedFile.value,
          mode: mode.value,
          project_id: projectId
        }

        const response = await axios.post(endpoint, payload)

        if (response.data.error === 'insufficient_credits') {
          handleInsufficientCredits(response.data.required_credits)
          return
        }

        // Handle successful response
        if (response.data.success) {
          messages.value.push({
            role: 'assistant',
            content: response.data.response
          })

          // If there's a warning, show it
          if (response.data.warning) {
            messages.value.push({
              role: 'assistant',
              content: `⚠️ Warning: ${response.data.warning}`
            })
          }

          // Refresh file list if in build mode
          if (mode.value === 'build') {
            await loadProjectFiles()
          }
        } else {
          throw new Error(response.data.error || 'Unknown error occurred')
        }

        await scrollToBottom()
      } catch (error) {
        console.error('Error sending message:', error)
        messages.value.push({
          role: 'assistant',
          content: `Error: ${error.response?.data?.error || error.message || 'An unknown error occurred'}`
        })
      } finally {
        isGenerating.value = false
        await scrollToBottom()
      }
    }

    const addNewFile = async () => {
      if (!newFileName.value) return

      try {
        const response = await axios.post('/api/builder/create-file/', {
          project_id: projectId,
          filename: newFileName.value
        })

        if (response.data.success) {
          selectedFile.value = newFileName.value
          await loadProjectFiles()
          newFileName.value = ''
        } else {
          throw new Error(response.data.error)
        }
      } catch (error) {
        console.error('Error creating file:', error)
        messages.value.push({
          role: 'assistant',
          content: `Error creating file: ${error.response?.data?.error || error.message}`
        })
      }
    }

    const handleFileUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      uploadedFileName.value = `Uploading ${file.name}...`

      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('project_id', projectId)

        const response = await axios.post('/api/builder/upload-file/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        if (response.data.success) {
          uploadedFileName.value = `${file.name} - Uploaded successfully`
          await loadProjectFiles()
          selectedFile.value = file.name
        } else {
          throw new Error(response.data.error)
        }
      } catch (error) {
        console.error('Error uploading file:', error)
        uploadedFileName.value = 'Error uploading file'
      }
    }

    const undoLastAction = async () => {
      if (!canUndo.value) return

      try {
        const response = await axios.post('/api/builder/undo-last-action/', {
          project_id: projectId,
          page: selectedFile.value
        })

        if (response.data.success) {
          // Remove the last assistant message
          const lastAssistantIndex = [...messages.value].reverse()
            .findIndex(m => m.role === 'assistant')
          if (lastAssistantIndex !== -1) {
            messages.value.splice(messages.value.length - lastAssistantIndex - 1, 1)
          }

          // Add undo confirmation message
          messages.value.push({
            role: 'assistant',
            content: 'Previous version restored successfully.'
          })

          // Refresh file list
          await loadProjectFiles()
        } else {
          throw new Error(response.data.error)
        }
      } catch (error) {
        console.error('Error undoing action:', error)
        messages.value.push({
          role: 'assistant',
          content: `Error undoing action: ${error.response?.data?.error || error.message}`
        })
      }
    }

    const previewProject = async () => {
      try {
        const response = await axios.post('/api/builder/preview-project/', {
          project_id: projectId
        })

        if (response.data.url) {
          window.open(response.data.url, '_blank')
        } else {
          throw new Error('Preview URL not found')
        }
      } catch (error) {
        console.error('Error starting preview:', error)
        messages.value.push({
          role: 'assistant',
          content: `Error previewing project: ${error.response?.data?.error || error.message}`
        })
      }
    }

    const useExamplePrompt = (prompt) => {
      userInput.value = prompt
      showWelcome.value = false
      sendMessage()
    }

    const loadConversation = (conversation) => {
      currentConversation.value = conversation
      // TODO: Load conversation messages
    }

    // Watchers
    watch(selectedFile, async (newFile) => {
      if (newFile === 'custom') return
      
      try {
        const response = await axios.get(`/api/builder/file-history/${projectId}/${newFile}/`)
        messages.value = response.data.messages
        showWelcome.value = false
      } catch (error) {
        console.error('Error loading file history:', error)
      }
    })

    // Lifecycle
    onMounted(async () => {
      // Restore sidebar state
      const savedCollapsed = localStorage.getItem('builderSidebarCollapsed')
      if (savedCollapsed !== null) {
        isSidebarCollapsed.value = savedCollapsed === 'true'
      }

      // Load initial data
      await Promise.all([
        loadProjectFiles(),
        loadConversationHistory()
      ])
    })

    return {
      // State
      isSidebarCollapsed,
      selectedModel,
      mode,
      selectedFile,
      newFileName,
      userInput,
      messages,
      isGenerating,
      showWelcome,
      uploadedFileName,
      conversations,
      currentConversation,
      examplePrompts,
      responseWindow,
      inputField,
      projectFiles,
      hasInsufficientCredits,
      requiredCredits,

      // Computed
      inputPlaceholder,
      canUndo,

      // Methods
      toggleSidebar,
      autoResizeInput,
      handleEnterKey,
      formatMessage,
      sendMessage,
      addNewFile,
      handleFileUpload,
      undoLastAction,
      previewProject,
      useExamplePrompt,
      loadConversation
    }
  }
}
</script>

<style>
@import '../assets/styles/builder_styles.css';
</style> 