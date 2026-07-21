<!--
  MarketingInbox.vue - Two-way SMS conversations: contacts with message
  history on the left, the selected thread with a reply box on the right.
-->
<template>
  <div>
    <!-- Loading -->
    <div v-if="store.conversationsLoading && !store.conversations.length" class="flex justify-center py-16">
      <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-700 dark:border-t-blue-300 rounded-full animate-spin motion-reduce:animate-none"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="!store.conversations.length && !thread" class="flex flex-col items-center justify-center py-20 text-center">
      <div class="w-16 h-16 text-2xl mb-5" :class="ui.iconTile">
        <i class="fas fa-inbox"></i>
      </div>
      <h2 class="text-xl font-semibold text-blue-950 dark:text-white mb-2">No conversations yet</h2>
      <p class="text-sm text-blue-950/60 dark:text-blue-100/60 max-w-md mb-2">
        Threads appear here once you message a contact or a customer texts your Twilio number.
      </p>
      <p v-if="needsWebhookHint" class="text-xs text-blue-950/50 dark:text-blue-100/50 max-w-md mb-6">
        To receive incoming texts, point your Twilio number's messaging webhook at Imagi — see the Settings tab.
      </p>
      <router-link
        :to="{ name: 'marketing-audience', params: { projectName: route.params.projectName } }"
        :class="ui.secondaryBtn"
        class="mt-2"
      >
        <i class="fas fa-address-book text-xs"></i>
        Go to audience
      </router-link>
    </div>

    <!-- Inbox -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      <!-- Conversation list -->
      <section class="overflow-hidden lg:max-h-[640px] flex flex-col" :class="ui.card">
        <div class="flex items-center justify-between px-4 py-3 border-b border-blue-200/60 dark:border-white/[0.08]">
          <h2 class="text-sm font-semibold text-blue-950 dark:text-white">Conversations</h2>
          <button
            type="button"
            class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/50 dark:text-blue-100/50 hover:text-blue-950 dark:hover:text-white hover:bg-blue-50 dark:hover:bg-white/[0.08] transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0c0c0e]"
            title="Refresh"
            @click="refresh"
          >
            <i class="fas fa-rotate text-xs" :class="{ 'animate-spin motion-reduce:animate-none': store.conversationsLoading }"></i>
          </button>
        </div>
        <div class="overflow-y-auto flex-1">
          <button
            v-for="conversation in store.conversations"
            :key="conversation.id"
            type="button"
            class="w-full flex items-start gap-3 px-4 py-3.5 text-left border-b border-blue-200/40 dark:border-white/[0.05] last:border-b-0 transition-colors duration-150 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50"
            :class="selectedId === conversation.id
              ? 'bg-blue-50/80 dark:bg-blue-400/10'
              : 'hover:bg-blue-50/60 dark:hover:bg-white/[0.04]'"
            @click="selectConversation(conversation.id)"
          >
            <div class="w-9 h-9 shrink-0 rounded-full flex items-center justify-center bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] text-blue-700 dark:text-blue-200 text-xs font-semibold uppercase">
              {{ initials(conversation.display_name) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2">
                <p class="text-sm font-medium text-blue-950 dark:text-white truncate">{{ conversation.display_name }}</p>
                <p class="text-[11px] text-blue-950/50 dark:text-blue-100/50 whitespace-nowrap">{{ formatDateTime(conversation.last_message_at) }}</p>
              </div>
              <p class="text-xs text-blue-950/60 dark:text-blue-100/60 truncate">
                <i
                  :class="['fas', conversation.last_message_direction === 'inbound' ? 'fa-reply' : 'fa-share', 'text-[10px] mr-1 opacity-60']"
                ></i>
                {{ conversation.last_message_body || '(no text)' }}
              </p>
            </div>
          </button>
        </div>
      </section>

      <!-- Thread -->
      <section class="lg:col-span-2 flex flex-col lg:max-h-[640px] min-h-[420px]" :class="ui.card">
        <template v-if="thread">
          <!-- Thread header -->
          <div class="flex items-center justify-between gap-3 px-5 py-3.5 border-b border-blue-200/60 dark:border-white/[0.08]">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-blue-950 dark:text-white truncate">{{ thread.contact.display_name }}</p>
              <p class="text-xs text-blue-950/50 dark:text-blue-100/50 font-mono">{{ thread.contact.phone_number }}</p>
            </div>
            <StatusBadge :status="thread.contact.consent" />
          </div>

          <!-- Messages -->
          <div ref="threadPane" class="flex-1 overflow-y-auto px-5 py-4 space-y-3">
            <div v-if="threadLoading" class="flex justify-center py-8">
              <div class="w-5 h-5 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-700 dark:border-t-blue-300 rounded-full animate-spin motion-reduce:animate-none"></div>
            </div>
            <template v-else>
              <div
                v-for="message in chronologicalMessages"
                :key="message.id"
                class="flex"
                :class="message.direction === 'outbound' ? 'justify-end' : 'justify-start'"
              >
                <div class="max-w-[78%]">
                  <div
                    class="px-3.5 py-2.5 rounded-2xl text-sm whitespace-pre-wrap break-words"
                    :class="message.direction === 'outbound'
                      ? 'bg-blue-950 text-[#fdf9f2] dark:bg-[#f3ede2] dark:text-blue-950 rounded-br-md'
                      : 'bg-blue-50 dark:bg-white/[0.08] text-blue-950 dark:text-white border border-blue-200/60 dark:border-white/[0.08] rounded-bl-md'"
                  >
                    <span v-if="message.channel === 'voice'" class="block text-[11px] uppercase tracking-wide opacity-70 mb-0.5">
                      <i class="fas fa-phone-volume mr-1"></i>Voice call
                    </span>
                    {{ message.body || '(no text)' }}
                  </div>
                  <p
                    class="text-[11px] text-blue-950/50 dark:text-blue-100/50 mt-1 px-1"
                    :class="message.direction === 'outbound' ? 'text-right' : ''"
                  >
                    {{ formatDateTime(message.created_at) }}
                    <template v-if="message.direction === 'outbound'"> · {{ message.status }}</template>
                    <template v-if="message.campaign_id"> · campaign</template>
                  </p>
                </div>
              </div>
            </template>
          </div>

          <!-- Reply box -->
          <div class="px-5 py-4 border-t border-blue-200/60 dark:border-white/[0.08]">
            <div v-if="thread.contact.consent !== 'subscribed'" :class="ui.infoBox">
              This contact unsubscribed (STOP). You can't message them unless they text START.
            </div>
            <form v-else class="flex items-end gap-3" @submit.prevent="sendReply">
              <textarea
                v-model="replyText"
                rows="2"
                maxlength="1600"
                placeholder="Type a reply..."
                class="resize-none"
                :class="ui.input"
                @keydown.enter.exact.prevent="sendReply"
              ></textarea>
              <button type="submit" :class="ui.primaryBtn" :disabled="sending || !replyText.trim()">
                <i :class="['fas', sending ? 'fa-circle-notch animate-spin motion-reduce:animate-none' : 'fa-paper-plane']" class="text-xs"></i>
                Send
              </button>
            </form>
            <p v-if="replyError" class="mt-2 text-xs text-red-600 dark:text-red-300">{{ replyError }}</p>
          </div>
        </template>

        <div v-else class="flex-1 flex flex-col items-center justify-center py-16 text-center px-6">
          <i class="fas fa-comments text-2xl text-blue-950/20 dark:text-blue-100/20 mb-4"></i>
          <p class="text-sm text-blue-950/60 dark:text-blue-100/60">Select a conversation to read and reply.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import StatusBadge from '../components/StatusBadge.vue'
import { extractError } from '../services/marketingService'
import { useMarketingStore } from '../stores/marketing'
import type { Contact, Message } from '../types'
import { formatDateTime, ui } from '../utils/ui'

const route = useRoute()
const store = useMarketingStore()

const selectedId = ref<number | null>(null)
const thread = ref<{ contact: Contact; messages: Message[] } | null>(null)
const threadLoading = ref(false)
const threadPane = ref<HTMLElement | null>(null)
const replyText = ref('')
const replyError = ref('')
const sending = ref(false)

const needsWebhookHint = computed(() => !store.settings?.inbound_webhook_url)

// API returns newest-first; the thread renders oldest-first.
const chronologicalMessages = computed(() => (thread.value ? [...thread.value.messages].reverse() : []))

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean)
  if (!parts.length) return '?'
  const first = parts[0]?.[0] ?? ''
  const last = parts.length > 1 ? parts[parts.length - 1]?.[0] ?? '' : ''
  return (first + last).slice(0, 2) || '#'
}

async function selectConversation(contactId: number) {
  selectedId.value = contactId
  threadLoading.value = true
  replyError.value = ''
  try {
    thread.value = await store.getThread(contactId)
    await scrollThreadToBottom()
  } catch (error) {
    replyError.value = extractError(error, 'Could not load the conversation.')
  } finally {
    threadLoading.value = false
  }
}

async function scrollThreadToBottom() {
  await nextTick()
  if (threadPane.value) {
    threadPane.value.scrollTop = threadPane.value.scrollHeight
  }
}

async function sendReply() {
  const body = replyText.value.trim()
  if (!body || !selectedId.value || sending.value) return
  sending.value = true
  replyError.value = ''
  try {
    const message = await store.sendDirectMessage(selectedId.value, body)
    replyText.value = ''
    if (thread.value) {
      thread.value.messages.unshift(message)
    }
    await scrollThreadToBottom()
    store.fetchConversations().catch(() => {})
  } catch (error) {
    replyError.value = extractError(error, 'Could not send the message.')
  } finally {
    sending.value = false
  }
}

async function refresh() {
  await store.fetchConversations()
  if (selectedId.value) {
    await selectConversation(selectedId.value)
  }
}

onMounted(async () => {
  try {
    await store.fetchConversations()
    // Deep link: /inbox?contact=123 opens that thread directly — even for a
    // contact with no history yet, so the first message can be sent here.
    const requested = Number(route.query.contact)
    const first = store.conversations[0]
    if (requested) {
      await selectConversation(requested)
    } else if (first) {
      await selectConversation(first.id)
    }
  } catch {
    // Empty state covers it.
  }
})
</script>
