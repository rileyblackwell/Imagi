<!--
  CampaignForm.vue - Campaign compose fields, shared by the "New campaign"
  modal and the draft editor on the campaign detail page.
-->
<template>
  <form class="space-y-5" @submit.prevent="submit">
    <!-- Name -->
    <div>
      <label :class="ui.label" for="campaign-name">Campaign name</label>
      <input
        id="campaign-name"
        v-model="form.name"
        type="text"
        required
        maxlength="255"
        placeholder="e.g. Grand opening announcement"
        :class="ui.input"
      />
    </div>

    <!-- Channel -->
    <div>
      <span :class="ui.label">Channel</span>
      <div class="grid grid-cols-2 gap-3">
        <button
          v-for="option in channelOptions"
          :key="option.value"
          type="button"
          class="flex items-start gap-3 p-3.5 rounded-xl border text-left transition-all duration-200"
          :class="form.channel === option.value
            ? 'border-violet-300 dark:border-violet-400/50 bg-violet-50/80 dark:bg-violet-400/10 ring-1 ring-violet-300/50 dark:ring-violet-400/30'
            : 'border-blue-200/70 dark:border-white/[0.12] bg-white dark:bg-white/[0.04] hover:border-violet-200 dark:hover:border-violet-400/30'"
          @click="form.channel = option.value"
        >
          <div class="w-9 h-9 shrink-0" :class="ui.iconTile">
            <i :class="['fas', option.icon]"></i>
          </div>
          <div>
            <p class="text-sm font-semibold text-blue-950 dark:text-white">{{ option.label }}</p>
            <p class="text-xs text-blue-950/60 dark:text-blue-100/60 leading-snug mt-0.5">{{ option.hint }}</p>
          </div>
        </button>
      </div>
    </div>

    <!-- Body -->
    <div>
      <label :class="ui.label" for="campaign-body">
        {{ form.channel === 'voice' ? 'Voice script' : 'Message' }}
      </label>
      <textarea
        id="campaign-body"
        v-model="form.body"
        required
        rows="4"
        :maxlength="1600"
        :placeholder="form.channel === 'voice'
          ? 'What the call should say, e.g. Hi {{first_name}}, our summer sale starts Friday...'
          : 'Hi {{first_name}}! Our summer sale starts Friday — reply for details.'"
        :class="ui.input"
      ></textarea>
      <div class="flex items-center justify-between mt-1.5 text-xs text-blue-950/50 dark:text-blue-100/50">
        <span>Personalize with <code class="font-mono">{{ '\{\{first_name\}\}' }}</code>, <code class="font-mono">{{ '\{\{last_name\}\}' }}</code>, <code class="font-mono">{{ '\{\{name\}\}' }}</code></span>
        <span v-if="form.channel === 'sms'">{{ form.body.length }}/1600 · ~{{ segmentCount }} segment{{ segmentCount === 1 ? '' : 's' }}</span>
      </div>
    </div>

    <!-- Audience -->
    <div>
      <span :class="ui.label">Audience</span>
      <div class="space-y-2.5">
        <label class="flex items-center gap-2.5 text-sm text-blue-950 dark:text-white cursor-pointer">
          <input v-model="form.audience_type" type="radio" value="all" class="accent-violet-600" />
          All subscribed contacts
        </label>
        <label class="flex items-center gap-2.5 text-sm text-blue-950 dark:text-white cursor-pointer">
          <input v-model="form.audience_type" type="radio" value="tags" class="accent-violet-600" />
          Contacts with any of these tags
        </label>
        <div v-if="form.audience_type === 'tags'" class="pl-6">
          <div v-if="tags.length" class="flex flex-wrap gap-2">
            <button
              v-for="tag in tags"
              :key="tag.tag"
              type="button"
              class="px-3 py-1.5 rounded-full border text-xs font-medium transition-all duration-200"
              :class="isTagSelected(tag.tag)
                ? 'border-violet-300 dark:border-violet-400/50 bg-violet-100/80 dark:bg-violet-400/20 text-violet-800 dark:text-violet-200'
                : 'border-blue-200/70 dark:border-white/[0.12] bg-white dark:bg-white/[0.04] text-blue-950/70 dark:text-blue-100/70 hover:border-violet-200 dark:hover:border-violet-400/30'"
              @click="toggleTag(tag.tag)"
            >
              {{ tag.tag }} <span class="opacity-60">· {{ tag.count }}</span>
            </button>
          </div>
          <p v-else class="text-xs text-blue-950/50 dark:text-blue-100/50">
            No tags yet — add tags to contacts in the Audience tab to segment your sends.
          </p>
        </div>
      </div>
    </div>

    <div v-if="error" :class="ui.errorBox">{{ error }}</div>

    <div class="flex items-center justify-end gap-3 pt-1">
      <button type="button" :class="ui.secondaryBtn" @click="$emit('cancel')">Cancel</button>
      <button type="submit" :class="ui.primaryBtn" :disabled="busy || !isValid">
        <i v-if="busy" class="fas fa-circle-notch animate-spin"></i>
        {{ submitLabel }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import type { Campaign, CampaignChannel, CampaignPayload, TagCount } from '../types'
import { ui } from '../utils/ui'

const props = defineProps<{
  initial?: Campaign | null
  tags: TagCount[]
  busy?: boolean
  error?: string
  submitLabel: string
}>()

const emit = defineEmits<{
  (e: 'submit', payload: CampaignPayload): void
  (e: 'cancel'): void
}>()

const channelOptions: { value: CampaignChannel; label: string; hint: string; icon: string }[] = [
  { value: 'sms', label: 'Text message', hint: 'SMS to each contact via Twilio Messaging', icon: 'fa-comment-sms' },
  { value: 'voice', label: 'Voice call', hint: 'A call that reads your script aloud', icon: 'fa-phone-volume' },
]

const form = reactive({
  name: props.initial?.name ?? '',
  channel: (props.initial?.channel ?? 'sms') as CampaignChannel,
  body: props.initial?.body ?? '',
  audience_type: props.initial?.audience_type ?? 'all',
  audience_tags: [...(props.initial?.audience_tags ?? [])],
})

const segmentCount = computed(() => Math.max(1, Math.ceil(form.body.length / 160)))

const isValid = computed(() => {
  if (!form.name.trim() || !form.body.trim()) return false
  if (form.audience_type === 'tags' && form.audience_tags.length === 0) return false
  return true
})

function isTagSelected(tag: string): boolean {
  return form.audience_tags.some(t => t.toLowerCase() === tag.toLowerCase())
}

function toggleTag(tag: string) {
  if (isTagSelected(tag)) {
    form.audience_tags = form.audience_tags.filter(t => t.toLowerCase() !== tag.toLowerCase())
  } else {
    form.audience_tags.push(tag)
  }
}

function submit() {
  if (!isValid.value) return
  emit('submit', {
    name: form.name.trim(),
    channel: form.channel,
    body: form.body,
    audience_type: form.audience_type,
    audience_tags: form.audience_type === 'tags' ? form.audience_tags : [],
  })
}
</script>
