<template>
  <div class="h-full flex flex-col relative z-10 transition-colors duration-300" :class="{'mode-transition': disableAllAnimations}">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-grow overflow-y-auto overflow-x-hidden px-4 py-6">
      <!-- Empty state -->
      <div v-if="!processedMessages.length" class="h-full flex flex-col items-center justify-center px-6 py-4 text-center min-h-0">
        <div class="empty-icon flex items-center justify-center w-12 h-12 rounded-2xl mb-4">
          <i class="fas fa-wand-magic-sparkles text-base"></i>
        </div>
        <h3 class="text-sm font-semibold text-blue-950/80 dark:text-white/85 mb-1.5">What should we build?</h3>
        <p class="text-xs text-blue-950/45 dark:text-white/40 max-w-[230px] leading-relaxed">
          Describe a page, feature, or change and the agent will build it into your project.
        </p>
      </div>
      
      <template v-if="processedMessages.length > 0">
        <div class="max-w-3xl mx-auto">
          <template v-for="(message, index) in processedMessages" :key="`msg-${message.id || index}`">
            <!-- User Message: a single compact bubble that opens the turn -->
            <div v-if="message.role === 'user'"
              class="msg-row user-row flex justify-end"
              :class="{ 'animate-message-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="user-bubble">
                <p class="whitespace-pre-wrap break-words text-sm leading-relaxed">{{ message.content }}</p>
              </div>
            </div>

            <!-- Assistant Message: the agent's work flows plainly below the bubble -->
            <div v-else-if="message.role === 'assistant'"
              class="msg-row assistant-response"
              :class="{ 'animate-message-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div
                class="prose prose-gray dark:prose-invert max-w-none prose-p:my-2 prose-headings:mb-3 prose-headings:mt-4 leading-relaxed text-sm"
                v-if="message.content && message.content.trim().length > 0"
                v-html="formatMessage(message.content)"
              />
            </div>

            <!-- System Message -->
            <div v-else-if="message.role === 'system'"
              class="msg-row flex justify-center"
              :class="{ 'animate-fade-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <span class="text-xs text-blue-950/40 dark:text-blue-100/40 px-3 py-1">{{ message.content }}</span>
            </div>

            <!-- Other message types -->
            <div v-else
              class="msg-row flex justify-center"
              :class="{ 'animate-message-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <span class="text-xs text-blue-950/40 dark:text-blue-100/40 px-3 py-1">{{ message.content }}</span>
            </div>
          </template>

          <!-- Agent activity indicator. Hidden while the reply itself is
               streaming in — the growing message already shows progress. -->
          <div v-if="showActivityIndicator" class="msg-row assistant-response animate-fade-in">
            <div class="agent-status flex items-center gap-2.5">
              <span class="status-orb"></span>
              <span class="status-shimmer text-sm font-medium">{{ props.statusText || 'Working…' }}</span>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import DOMPurify from 'isomorphic-dompurify'
import { ref, onUpdated, nextTick, watch, onMounted, computed } from 'vue'
import type { AIMessage } from '@/apps/imagi/build/types/services'

// Extended AIMessage interface to include isNew flag
interface ProcessedMessage extends AIMessage {
  isNew?: boolean;
  isTyping?: boolean;
}

const props = defineProps<{
  messages: AIMessage[]
  isProcessing?: boolean
  /** What the agent is doing right now; empty while its reply is streaming. */
  statusText?: string
}>()

/**
 * Show the activity indicator while the agent works, except when the reply is
 * actively streaming (last message is the assistant's, growing in place) and
 * nothing else is going on — then the indicator would just dangle beneath it.
 * A tool call mid-run sets statusText again, which brings the indicator back.
 */
const showActivityIndicator = computed(() => {
  if (!props.isProcessing) return false
  if (props.statusText) return true
  const last = props.messages[props.messages.length - 1]
  return !(last?.role === 'assistant' && (last.content || '').trim().length > 0)
})

const emit = defineEmits<{
  (e: 'apply-code', code: string): void
  (e: 'use-example', example: string): void
}>()

// Refs and reactive state
const messagesContainer = ref<HTMLElement | null>(null)
const isTyping = ref(false)
const previousMessageCount = ref(0)
const disableAllAnimations = ref(false)

// Process messages to add isNew flag for animations
const processedMessages = computed<ProcessedMessage[]>(() => {
  return props.messages.map((message, index) => {
    // Only mark messages as new if they're newly added and animations
    // aren't globally disabled
    const isNew = (index >= previousMessageCount.value)
      && !disableAllAnimations.value;

    return {
      ...message,
      isNew
    };
  });
});

// Update previousMessageCount after rendering
watch(() => props.messages.length, (newLength) => {
  // Only update the animation state after rendering is complete
  nextTick(() => {
    // Keep track of previous length to identify new messages
    previousMessageCount.value = newLength;
    scrollToBottom();
  });
}, { immediate: true });

// Also scroll on component update
onUpdated(() => {
  nextTick(() => {
    scrollToBottom()
  })
})

// Monitor message changes for content changes too (not just length)
watch(() => JSON.stringify(props.messages), () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// When the last message is from the user and there's no AI response yet, show typing indicator
watch(() => props.messages, (messages) => {
  if (messages.length > 0) {
    const lastMessage = messages[messages.length - 1]
    // Only show typing indicator if not currently processing
    isTyping.value = lastMessage?.role === 'user' && !props.isProcessing
  } else {
    isTyping.value = false
  }
}, { immediate: true, deep: true })

// Also watch processing state to update typing indicator
watch(() => props.isProcessing, () => {
  if (props.messages.length > 0) {
    const lastMessage = props.messages[props.messages.length - 1]
    // When processing starts, turn off normal typing indicator
    isTyping.value = lastMessage?.role === 'user' && !props.isProcessing
  }
})

// Initial scroll when component is mounted
onMounted(() => {
  nextTick(() => {
    // Initialize previous message count
    previousMessageCount.value = props.messages.length;
    scrollToBottom()
  })
})

function scrollToBottom() {
  if (messagesContainer.value) {
    const container = messagesContainer.value
    // Force scroll to bottom with animation
    container.scrollTo({
      top: container.scrollHeight,
      behavior: 'smooth'
    })
  }
}

// Utility functions
const formatTimestamp = (timestamp: string | number) => {
  if (!timestamp) return ''
  
  try {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    return ''
  }
}

// Helper function to format markdown content
const formatMessage = (content: string) => {
  if (!content) {
    return '';
  }
  
  try {
    // Remove any code blocks from the content before rendering
    const contentWithoutCode = content.replace(/```[\s\S]*?```/g, '');
    
    // Configure marked options
    marked.setOptions({
      gfm: true,
      breaks: true,
    });

    // Parse markdown with type assurance
    const parsedContent = marked.parse(contentWithoutCode).toString();
    
    // Sanitize the content to prevent XSS
    return DOMPurify.sanitize(parsedContent);
  } catch (e) {
    console.error('Error parsing markdown:', e)
    return content
  }
}

const copyToClipboard = (code: string) => {
  navigator.clipboard.writeText(code)
    .then(() => {
      console.log('Code copied to clipboard')
    })
    .catch(err => {
      console.error('Could not copy code:', err)
    })
}
</script>

<style scoped>
/* Vertical rhythm: messages within a turn sit close together, and each new
   user bubble opens a turn with extra breathing room above it. */
.msg-row + .msg-row {
  margin-top: 1rem;
}

.msg-row + .user-row {
  margin-top: 2rem;
}

/* The user's prompt is the one element that gets a bubble */
.user-bubble {
  max-width: 85%;
  padding: 0.625rem 0.875rem;
  border-radius: 1rem;
  border-bottom-right-radius: 0.375rem;
  background-color: theme('colors.blue.50');
  border: 1px solid rgba(191, 219, 254, 0.6);
  color: theme('colors.blue.950');
  /* Long unbroken strings (paths, URLs) wrap instead of widening the chat
     and dragging in a horizontal scrollbar. */
  overflow-wrap: anywhere;
  min-width: 0;
}

.dark .user-bubble {
  background-color: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.92);
}

/* The agent's work flows directly on the panel background — no box, no label */
.assistant-response {
  font-size: 0.875rem;
  line-height: 1.6;
  /* Code blocks keep their own overflow-x so they scroll within their box,
     not the page. */
  overflow-wrap: anywhere;
  min-width: 0;
}

/* Prose styling */
.prose {
  font-size: 0.875rem;
  line-height: 1.6;
  color: theme('colors.blue.950');
}

.dark .prose {
  color: rgba(219, 234, 254, 0.85);
}

.prose pre {
  background: theme('colors.slate.50');
  border: 1px solid rgba(203, 213, 225, 0.6);
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.dark .prose pre {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.prose code {
  color: theme('colors.orange.700');
  background: theme('colors.orange.50');
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  border: 1px solid rgba(254, 215, 170, 0.7);
}

.dark .prose code {
  color: theme('colors.orange.300');
  background: rgba(251, 146, 60, 0.1);
  border: 1px solid rgba(251, 146, 60, 0.2);
}

/* Wide tables scroll within their own box; the container clips overflow, so
   without this their far columns would be cut off with no way to reach them. */
.prose table {
  display: block;
  max-width: 100%;
  overflow-x: auto;
}

.prose p {
  margin-bottom: 0.75rem;
}

.prose p:last-child {
  margin-bottom: 0;
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: theme('colors.blue.950');
}

.dark .prose h1, .dark .prose h2, .dark .prose h3, .dark .prose h4 {
  color: theme('colors.white');
}

.prose ul, .prose ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

/* Message animations */
@keyframes message-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-message-in {
  animation: message-in 0.3s ease-out forwards;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out forwards;
}

/* Minimal scrollbar */
.overflow-y-auto {
  scrollbar-width: thin;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.15);
}

:root.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
}

:root.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Agent activity indicator: a softly breathing orb next to status text with
   a light shimmer sweeping across it. */
.status-orb {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #93c5fd, #3b82f6);
  box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.35);
  animation: orb-breathe 2s ease-in-out infinite;
}

.dark .status-orb {
  background: radial-gradient(circle at 30% 30%, #bfdbfe, #60a5fa);
  box-shadow: 0 0 0 0 rgba(147, 197, 253, 0.3);
}

@keyframes orb-breathe {
  0%, 100% {
    transform: scale(0.9);
    box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.35);
  }
  50% {
    transform: scale(1);
    box-shadow: 0 0 0 5px rgba(59, 130, 246, 0);
  }
}

.status-shimmer {
  background-image: linear-gradient(
    100deg,
    rgba(23, 37, 84, 0.4) 20%,
    rgba(59, 130, 246, 0.95) 50%,
    rgba(23, 37, 84, 0.4) 80%
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: shimmer-sweep 2.2s linear infinite;
}

.dark .status-shimmer {
  background-image: linear-gradient(
    100deg,
    rgba(255, 255, 255, 0.35) 20%,
    rgba(255, 255, 255, 0.95) 50%,
    rgba(255, 255, 255, 0.35) 80%
  );
  background-size: 200% 100%;
}

@keyframes shimmer-sweep {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (prefers-reduced-motion: reduce) {
  .status-orb,
  .status-shimmer {
    animation: none;
  }

  .status-shimmer {
    background-clip: unset;
    -webkit-background-clip: unset;
    background-image: none;
    color: rgba(23, 37, 84, 0.55);
  }

  .dark .status-shimmer {
    color: rgba(255, 255, 255, 0.6);
  }
}

/* Empty state icon: soft baby-blue tile matching the site's primary button */
.empty-icon {
  color: theme('colors.blue.900');
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.12),
    0 6px 14px -4px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75);
}

.dark .empty-icon {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 6px 14px -4px rgba(0, 0, 0, 0.45),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.6);
}

/* Prose styling for dark mode */
.prose-invert h1,
.prose-invert h2,
.prose-invert h3,
.prose-invert h4,
.prose-invert h5,
.prose-invert h6 {
  color: theme('colors.white');
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.prose-invert p {
  color: rgba(219, 234, 254, 0.8);
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.prose-invert p:last-child {
  margin-bottom: 0;
}

.prose-invert strong {
  color: theme('colors.white');
  font-weight: 600;
}

.prose-invert code {
  color: theme('colors.orange.300');
  background-color: rgba(251, 146, 60, 0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid rgba(251, 146, 60, 0.2);
}

.prose-invert blockquote {
  color: rgba(191, 219, 254, 0.7);
  border-left-color: rgba(59, 130, 246, 0.5);
  border-left-width: 4px;
  padding-left: 1rem;
  font-style: italic;
  margin: 1rem 0;
}

.prose-invert ul,
.prose-invert ol {
  color: rgba(219, 234, 254, 0.8);
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose-invert li {
  margin: 0.375rem 0;
  line-height: 1.5;
}

.prose-invert a {
  color: theme('colors.blue.300');
  text-decoration: underline;
  text-decoration-color: rgba(147, 197, 253, 0.4);
}

.prose-invert a:hover {
  color: theme('colors.blue.200');
  text-decoration-color: rgba(191, 219, 254, 0.6);
}
</style> 