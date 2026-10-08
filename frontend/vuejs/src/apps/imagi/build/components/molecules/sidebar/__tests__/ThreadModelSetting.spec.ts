import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import ThreadModelSetting from '../ThreadModelSetting.vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import type { AgentInstance } from '@/apps/imagi/build/types/services'

vi.mock('@/apps/imagi/build/services/agentService', () => ({
  AgentService: { updateConversation: vi.fn().mockResolvedValue({}) },
}))

const thread = (id: string, model: string): AgentInstance => ({
  id,
  conversationId: Number(id.replace(/\D/g, '')) || 1,
  title: 'Thread',
  kind: 'task',
  parentId: 1,
  reviewStatus: 'active',
  variantGroup: '',
  hasWorktree: true,
  totalTokens: null,
  selectedModelId: model,
  selectedEffort: 'medium',
  selectedFile: null,
  conversation: [],
  isProcessing: false,
  statusText: '',
  archivedAt: null,
  updatedAt: new Date().toISOString(),
  lastMessagePreview: '',
  lastAssistantSummary: '',
  brief: '',
  overview: '',
  messagesLoaded: true,
  hasUnread: false,
  queuedPrompt: null,
})

describe('ThreadModelSetting', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  it('names the model threads run on, Opus 5.5 to begin with', () => {
    const wrapper = mount(ThreadModelSetting)
    expect(wrapper.find('.control-chip').text()).toBe('Opus 5.5')
  })

  it('picks the model for new threads from the menu', async () => {
    const wrapper = mount(ThreadModelSetting)
    await wrapper.find('.control-chip').trigger('click')
    const rows = wrapper.findAll('.model-row')
    expect(rows.map(r => r.find('.model-row__name').text())).toEqual([
      'Luna Fast', 'Opus 5.5 Balanced', 'Astra Frontier',
    ])
    await rows[0]!.trigger('click')
    expect(useAgentStore().threadModelId).toBe('gpt-6-luna')
    expect(wrapper.find('.control-chip').text()).toBe('Luna')
  })

  it('offers to switch the threads on another model, and does', async () => {
    const store = useAgentStore()
    store.instances = [thread('t1', 'gpt-6-astra'), thread('t2', 'claude-opus-5-5')]
    const wrapper = mount(ThreadModelSetting)
    await wrapper.find('.control-chip').trigger('click')

    const switchAll = wrapper.find('.thread-model__switch')
    expect(switchAll.text()).toBe('Switch 1 thread to Opus 5.5')
    await switchAll.trigger('click')

    expect(store.instances.every(i => i.selectedModelId === 'claude-opus-5-5')).toBe(true)
    expect(wrapper.find('.thread-model__switch').exists()).toBe(false)
    expect(wrapper.text()).toContain('Every thread is on Opus 5.5.')
  })
})
