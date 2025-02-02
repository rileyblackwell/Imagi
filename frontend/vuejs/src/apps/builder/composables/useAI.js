import { ref, computed } from 'vue';
import axios from 'axios';
import { useProjects } from './useProjects';

const conversation = ref([]);
const isGenerating = ref(false);
const error = ref(null);
const credits = ref(null);

export function useAI() {
  const { currentProject } = useProjects();

  /**
   * Send a prompt to the AI and get a response
   * @param {Object} promptData - The prompt data
   * @param {string} promptData.prompt - The user's prompt
   * @param {string} promptData.context - Additional context for the AI
   * @param {string} promptData.mode - The interaction mode ('chat' or 'build')
   */
  async function sendPrompt(promptData) {
    isGenerating.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/ai/generate/', {
        ...promptData,
        project_id: currentProject.value?.id
      });

      conversation.value.push({
        role: 'user',
        content: promptData.prompt,
        timestamp: new Date().toISOString()
      });

      conversation.value.push({
        role: 'assistant',
        content: response.data.response,
        code: response.data.code,
        timestamp: new Date().toISOString()
      });

      // Update remaining credits
      credits.value = response.data.credits_remaining;

      return response.data;
    } catch (err) {
      console.error('AI generation failed:', err);
      error.value = err.response?.data?.message || 'Failed to generate response. Please try again.';
      throw err;
    } finally {
      isGenerating.value = false;
    }
  }

  /**
   * Clear the conversation history
   */
  function clearConversation() {
    conversation.value = [];
  }

  /**
   * Get conversation history for a project
   * @param {string} projectId - The ID of the project
   */
  async function fetchConversationHistory(projectId) {
    isGenerating.value = true;
    error.value = null;

    try {
      const response = await axios.get(`/api/ai/history/${projectId}/`);
      conversation.value = response.data;
    } catch (err) {
      console.error('Failed to fetch conversation history:', err);
      error.value = err.response?.data?.message || 'Failed to fetch conversation history. Please try again.';
    } finally {
      isGenerating.value = false;
    }
  }

  /**
   * Get remaining AI credits for the user
   */
  async function fetchCredits() {
    try {
      const response = await axios.get('/api/ai/credits/');
      credits.value = response.data.credits;
    } catch (err) {
      console.error('Failed to fetch credits:', err);
      error.value = err.response?.data?.message || 'Failed to fetch credits. Please try again.';
    }
  }

  /**
   * Apply AI-generated code changes to the project
   * @param {Object} changes - The code changes to apply
   * @param {string} changes.file_path - The path to the file to modify
   * @param {string} changes.content - The new content for the file
   */
  async function applyCodeChanges(changes) {
    isGenerating.value = true;
    error.value = null;

    try {
      const response = await axios.post(`/api/ai/apply/${currentProject.value?.id}/`, changes);
      return response.data;
    } catch (err) {
      console.error('Failed to apply code changes:', err);
      error.value = err.response?.data?.message || 'Failed to apply code changes. Please try again.';
      throw err;
    } finally {
      isGenerating.value = false;
    }
  }

  /**
   * Get suggestions for code improvements
   * @param {string} filePath - The path to the file to analyze
   */
  async function getCodeSuggestions(filePath) {
    isGenerating.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/ai/suggest/', {
        project_id: currentProject.value?.id,
        file_path: filePath
      });
      return response.data.suggestions;
    } catch (err) {
      console.error('Failed to get code suggestions:', err);
      error.value = err.response?.data?.message || 'Failed to get code suggestions. Please try again.';
      throw err;
    } finally {
      isGenerating.value = false;
    }
  }

  // Computed properties
  const conversationHistory = computed(() => conversation.value);
  const generating = computed(() => isGenerating.value);
  const aiError = computed(() => error.value);
  const remainingCredits = computed(() => credits.value);

  return {
    // State
    conversation: conversationHistory,
    isGenerating: generating,
    error: aiError,
    credits: remainingCredits,

    // Methods
    sendPrompt,
    clearConversation,
    fetchConversationHistory,
    fetchCredits,
    applyCodeChanges,
    getCodeSuggestions
  };
} 