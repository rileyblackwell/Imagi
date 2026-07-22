<template>
  <div class="h-full flex flex-col relative z-10 transition-colors duration-300" :class="{'mode-transition': disableAllAnimations}">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-grow overflow-y-auto overflow-x-hidden px-4 py-6">
      <!-- Empty state -->
      <div v-if="!processedMessages.length" class="h-full flex flex-col items-center justify-center px-6 py-4 text-center min-h-0">
        <div class="empty-icon flex items-center justify-center w-12 h-12 rounded-2xl mb-4">
          <i class="fas fa-wand-magic-sparkles text-base"></i>
        </div>
        <h3 class="text-sm font-semibold text-blue-950 dark:text-white mb-1.5">What should we build?</h3>
        <p class="text-xs text-blue-950/45 dark:text-blue-100/45 max-w-[230px] leading-relaxed">
          Describe a page, feature, or change and the agent will build it into your project.
        </p>
        <div v-if="examples?.length" class="mt-4 flex flex-col items-stretch gap-1.5 w-full max-w-[240px]">
          <button
            v-for="example in examples"
            :key="example"
            type="button"
            class="rounded-full border border-blue-100 dark:border-white/[0.08] bg-blue-50/50 dark:bg-white/[0.04] px-3 py-1.5 text-[11px] font-medium text-blue-950/70 dark:text-white/65 hover:bg-blue-50 hover:text-blue-950 dark:hover:bg-white/[0.08] dark:hover:text-white transition-colors truncate"
            @click="emit('use-example', example)"
          >
            {{ example }}
          </button>
        </div>
      </div>
      
      <template v-if="processedMessages.length > 0">
        <div class="max-w-3xl mx-auto">
          <template v-for="(message, index) in processedMessages" :key="`msg-${message.id || index}`">
            <!-- User Message: a single compact bubble that opens the turn -->
            <div v-if="message.role === 'user'"
              class="msg-row user-row group flex flex-col items-end"
              :class="{ 'animate-message-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="user-bubble">
                <p class="whitespace-pre-wrap break-words text-sm leading-relaxed">{{ message.content }}</p>
              </div>
              <!-- Checkpoint: rewind files + conversation to just before this
                   message. Revealed on hover/focus so the transcript stays
                   quiet. Restore chips belong to canonical-tree threads
                   (chat/lead) and hide while a canonical run is live — the
                   parent gates both via can-restore; task transcripts never
                   show them. -->
              <button
                v-if="message.checkpoint && message.dbId && restoreAllowed"
                type="button"
                class="restore-chip mt-1 inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] font-medium text-blue-950/40 dark:text-white/35 hover:text-blue-950/75 dark:hover:text-white/75 hover:bg-blue-50/80 dark:hover:bg-white/[0.06] opacity-0 group-hover:opacity-100 focus-visible:opacity-100 transition-opacity duration-150"
                title="Restore your app and this conversation to the moment before this message"
                @click="emit('restore-checkpoint', message)"
              >
                <i class="fas fa-clock-rotate-left text-[9px]"></i>
                Restore checkpoint
              </button>
            </div>

            <!-- Assistant Message: the agent's work flows plainly below the bubble -->
            <div v-else-if="message.role === 'assistant'"
              class="msg-row assistant-response"
              :class="{ 'animate-message-in': message.isNew }"
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <AgentActivityFeed
                v-if="message.activity?.length"
                :steps="message.activity"
                :streaming="isStreamingMessage(index)"
                class="mb-2.5"
              />
              <AgentPlanChecklist
                v-if="message.plan?.length"
                :steps="message.plan"
                class="mb-2.5"
              />
              <div
                class="prose prose-gray dark:prose-invert max-w-none prose-p:my-2 prose-headings:mb-3 prose-headings:mt-4 leading-relaxed text-sm"
                v-if="message.content && message.content.trim().length > 0"
                v-html="formatMessage(message, index)"
              />
              <div v-if="message.filesChanged?.length" class="mt-2">
                <span
                  class="inline-flex items-center gap-1.5 rounded-full border border-blue-100 dark:border-white/[0.08] bg-blue-50/60 dark:bg-white/[0.04] px-2.5 py-1 text-[11px] font-medium text-blue-950/70 dark:text-white/60"
                  :title="message.filesChanged.join('\n')"
                >
                  <i class="fas fa-file-pen text-[9px] text-blue-600/70 dark:text-blue-300/70"></i>
                  {{ message.filesChanged.length }} {{ message.filesChanged.length === 1 ? 'file' : 'files' }} updated
                </span>
              </div>
              <!-- Run token usage: outside the memoized v-html, so its late
                   arrival (on done) never needs a cache invalidation. Renders
                   only when tokens were captured — absent usage is unknown,
                   never "0 tokens". -->
              <p
                v-if="typeof messageTokens(message) === 'number'"
                class="mt-1.5 text-[10px] text-blue-950/35 dark:text-white/30"
              >
                {{ formatTokens(messageTokens(message)!) }}
              </p>
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
import { ref, nextTick, watch, onMounted, onBeforeUnmount, computed } from 'vue'
import type { AIMessage } from '@/apps/imagi/build/types/services'
import AgentActivityFeed from '@/apps/imagi/build/components/molecules/chat/AgentActivityFeed.vue'
import AgentPlanChecklist from '@/apps/imagi/build/components/molecules/chat/AgentPlanChecklist.vue'

marked.setOptions({
  gfm: true,
  breaks: true,
})

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
  /** Starter prompts offered in the empty state; clicking one emits use-example. */
  examples?: string[]
  /** Whether restore chips may show: false on task transcripts (their edits
   *  live in a worktree, not the canonical timeline) and while a
   *  canonical-tree run is live. Omitted = fall back to !isProcessing. */
  canRestore?: boolean
}>()

const restoreAllowed = computed(() =>
  props.canRestore !== undefined ? props.canRestore : !props.isProcessing
)

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
  (e: 'restore-checkpoint', message: AIMessage): void
}>()

// Refs and reactive state
const messagesContainer = ref<HTMLElement | null>(null)
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

/** The reply currently streaming in is the last message while a run is active. */
function isStreamingMessage(index: number): boolean {
  return !!props.isProcessing && index === props.messages.length - 1
}

// --- Autoscroll ---------------------------------------------------------
// Only follow the conversation while the user is pinned near the bottom;
// scrolling up to read pauses following until they return.
const PIN_THRESHOLD_PX = 80
const isPinnedToBottom = ref(true)

function handleScroll() {
  const el = messagesContainer.value
  if (!el) return
  isPinnedToBottom.value = el.scrollHeight - el.scrollTop - el.clientHeight <= PIN_THRESHOLD_PX
}

// rAF-throttled: at most one scroll per frame, measured after Vue has
// patched the DOM (render flush happens in a microtask, before the frame).
let scrollFrame: number | null = null
function scheduleScrollToBottom(behavior: ScrollBehavior) {
  if (scrollFrame !== null) return
  scrollFrame = requestAnimationFrame(() => {
    scrollFrame = null
    const el = messagesContainer.value
    if (!el) return
    if (typeof el.scrollTo === 'function') {
      el.scrollTo({ top: el.scrollHeight, behavior })
    } else {
      // jsdom (tests) has no Element#scrollTo
      el.scrollTop = el.scrollHeight
    }
  })
}

function followConversation() {
  if (isPinnedToBottom.value) {
    // Instant jumps while streaming; smooth for one-off additions
    scheduleScrollToBottom(props.isProcessing ? 'auto' : 'smooth')
  }
}

// New messages: track the count for entry animations, then follow
watch(() => props.messages.length, (newLength) => {
  // Only update the animation state after rendering is complete
  nextTick(() => {
    previousMessageCount.value = newLength
    followConversation()
  })
}, { immediate: true })

// Streaming deltas: watch the last message's size instead of deep-watching
// (and re-serializing) the whole conversation on every SSE event. Activity
// steps count too so the feed growing keeps the view pinned.
watch(() => {
  const last = props.messages[props.messages.length - 1]
  return `${last?.content?.length ?? 0}:${last?.activity?.length ?? 0}`
}, () => {
  followConversation()
})

// Initial scroll when component is mounted
onMounted(() => {
  messagesContainer.value?.addEventListener('scroll', handleScroll, { passive: true })
  nextTick(() => {
    // Initialize previous message count
    previousMessageCount.value = props.messages.length
    scheduleScrollToBottom('auto')
  })
})

onBeforeUnmount(() => {
  messagesContainer.value?.removeEventListener('scroll', handleScroll)
  if (scrollFrame !== null) {
    cancelAnimationFrame(scrollFrame)
    scrollFrame = null
  }
})

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

// Rendered-HTML cache: markdown parsing + sanitization run once per
// (message, size), so a streaming delta only re-renders the growing message
// instead of the whole conversation. Never evicted — conversations are
// bounded, and stale keys are just unused strings. The source content is
// stored alongside the HTML and verified on hit: end-of-run reconciliation
// rewrites a message wholesale, and the corrected text can collide with a
// previously rendered prefix of the same length.
const renderedHtmlCache = new Map<string, { content: string; html: string }>()

const formatMessage = (message: AIMessage, index: number): string => {
  const content = message.content || ''
  if (!content) {
    return ''
  }

  // Same identity fallback as the template's v-for key
  const cacheKey = `${message.id || index}:${content.length}`
  const cached = renderedHtmlCache.get(cacheKey)
  if (cached !== undefined && cached.content === content) {
    return cached.html
  }

  let html: string
  try {
    // Parse markdown (fenced code included) and sanitize to prevent XSS
    html = DOMPurify.sanitize(marked.parse(content).toString())
  } catch (e) {
    console.error('Error parsing markdown:', e)
    html = DOMPurify.sanitize(content)
  }
  renderedHtmlCache.set(cacheKey, { content, html })
  return html
}

/**
 * Total tokens a reply used, or null when its usage was never captured
 * (absent means unknown, never free — and an all-zero total also renders
 * nothing rather than a misleading "0 tokens").
 */
const messageTokens = (message: AIMessage): number | null => {
  const usage = message.usage
  if (!usage) return null
  const input = typeof usage.inputTokens === 'number' ? usage.inputTokens : null
  const output = typeof usage.outputTokens === 'number' ? usage.outputTokens : null
  if (input === null && output === null) return null
  const total = (input ?? 0) + (output ?? 0)
  return total > 0 ? total : null
}

/** Tiny usage caption under a reply, e.g. "9,340 tokens", "12.3k tokens". */
const formatTokens = (total: number): string => {
  if (total >= 1_000_000) {
    const millions = total / 1_000_000
    return `${millions >= 10 ? Math.round(millions) : Math.round(millions * 10) / 10}M tokens`
  }
  if (total > 10_000) {
    const thousands = total / 1_000
    return `${thousands >= 100 ? Math.round(thousands) : Math.round(thousands * 10) / 10}k tokens`
  }
  return `${total.toLocaleString()} tokens`
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

/* Touch screens have no hover: keep the restore chip faintly visible so the
   affordance is discoverable without a pointer. */
@media (hover: none) {
  .restore-chip {
    opacity: 0.55;
  }
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

/* Markdown children arrive via v-html and never get the scope attribute,
   so anything targeting them needs :deep. Fenced code renders as a quiet
   navy-ink chip that scrolls within its own box. */
.prose :deep(pre) {
  background: rgba(239, 246, 255, 0.6);
  border: 1px solid theme('colors.blue.100');
  border-radius: 0.625rem;
  padding: 0.75rem 0.875rem;
  margin: 0.75rem 0;
  overflow-x: auto;
  font-size: 0.75rem;
  line-height: 1.6;
  color: theme('colors.blue.950');
}

.dark .prose :deep(pre) {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.85);
}

.prose :deep(code) {
  color: theme('colors.orange.700');
  background: theme('colors.orange.50');
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  border: 1px solid rgba(254, 215, 170, 0.7);
}

.dark .prose :deep(code) {
  color: theme('colors.orange.300');
  background: rgba(251, 146, 60, 0.1);
  border-color: rgba(251, 146, 60, 0.2);
}

/* The typography plugin wraps inline code in backticks — the chip already
   says "code" */
.prose :deep(code::before),
.prose :deep(code::after) {
  content: none;
}

/* Inside a fenced block the inline-code pill styling resets away */
.prose :deep(pre code),
.dark .prose :deep(pre code) {
  display: block;
  background: transparent;
  border: none;
  padding: 0;
  color: inherit;
  font-size: inherit;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

/* Wide tables scroll within their own box; the container clips overflow, so
   without this their far columns would be cut off with no way to reach them. */
.prose :deep(table) {
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

/* Ink-tinted links instead of the typography plugin's gray */
.prose a {
  color: theme('colors.blue.700');
}

.dark .prose a {
  color: theme('colors.blue.300');
}

/* Ink-tinted list markers instead of the typography plugin's gray */
.prose ::marker {
  color: rgba(23, 37, 84, 0.4);
}

.dark .prose ::marker {
  color: rgba(219, 234, 254, 0.4);
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
  .status-shimmer,
  .animate-message-in,
  .animate-fade-in {
    animation: none;
  }

  .status-shimmer {
    background-clip: unset;
    -webkit-background-clip: unset;
    background-image: none;
    color: rgba(23, 37, 84, 0.55);
  }

  .dark .status-shimmer {
    color: rgba(219, 234, 254, 0.65);
  }
}

/* Empty state icon: navy ink tile matching the site's primary button */
.empty-icon {
  color: #fdf9f2;
  background: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.2),
    0 6px 14px -4px rgba(23, 37, 84, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.dark .empty-icon {
  color: theme('colors.blue.950');
  background: #f3ede2;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 6px 14px -4px rgba(0, 0, 0, 0.45);
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