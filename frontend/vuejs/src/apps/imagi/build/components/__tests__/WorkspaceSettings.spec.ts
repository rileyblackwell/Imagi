import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount, type VueWrapper } from '@vue/test-utils'
import { nextTick } from 'vue'
import { setActivePinia, createPinia } from 'pinia'
import WorkspaceSettings from '../organisms/workspace/WorkspaceSettings.vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import { useWorkspaceSettings } from '@/apps/imagi/build/composables/useWorkspaceSettings'
import type { AgentInstance } from '@/apps/imagi/build/types/services'

vi.mock('@/apps/imagi/build/services/agentService', () => ({
  AgentService: { updateConversation: vi.fn().mockResolvedValue({}) },
}))

const agent = (id: string, kind: 'lead' | 'task', model: string): AgentInstance => ({
  id,
  conversationId: Number(id.replace(/\D/g, '')) || 1,
  title: '',
  kind,
  parentId: null,
  reviewStatus: kind === 'task' ? 'active' : '',
  variantGroup: '',
  hasWorktree: kind === 'task',
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

describe('WorkspaceSettings', () => {
  let wrapper: VueWrapper | null = null
  const panel = () => document.body.querySelector('[role="dialog"]')
  const groups = () => Array.from(document.body.querySelectorAll<HTMLElement>('[role="radiogroup"]'))
  const checked = (group: HTMLElement) =>
    group.querySelector('[aria-checked="true"] .choice-segments__name')?.textContent?.trim()
  const option = (group: HTMLElement, name: string) =>
    Array.from(group.querySelectorAll<HTMLButtonElement>('button')).find(b => b.textContent?.includes(name))!

  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    useWorkspaceSettings().closeSettings()
  })
  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  async function openWith(instances: AgentInstance[]) {
    const store = useAgentStore()
    store.instances = instances
    wrapper = mount(WorkspaceSettings, { attachTo: document.body })
    useWorkspaceSettings().openSettings()
    await nextTick()
    return store
  }

  it('stays shut until the gear opens it, and closes again', async () => {
    wrapper = mount(WorkspaceSettings, { attachTo: document.body })
    expect(panel()).toBeNull()
    useWorkspaceSettings().openSettings()
    await nextTick()
    expect(panel()?.textContent).toContain('Workspace settings')
    ;(document.body.querySelector('[aria-label="Close settings"]') as HTMLButtonElement).click()
    await nextTick()
    expect(useWorkspaceSettings().open.value).toBe(false)
  })

  it('has no coordinator model: only the thread defaults, Opus 5.5 on Medium', async () => {
    await openWith([agent('lead1', 'lead', 'claude-opus-5-5')])
    const [model, effort, ...rest] = groups()
    expect(rest).toHaveLength(0)
    expect(panel()?.textContent).not.toContain('Coordinator')
    expect(model!.getAttribute('aria-label')).toBe('Thread model')
    expect(checked(model!)).toBe('Opus 5.5')
    expect(effort!.getAttribute('aria-label')).toBe('Thread effort')
    expect(checked(effort!)).toBe('Medium')
  })

  it('saves the thread model and effort on the coordinator, leaving its own model alone', async () => {
    const { AgentService } = await import('@/apps/imagi/build/services/agentService')
    const store = await openWith([agent('lead1', 'lead', 'claude-opus-5-5')])
    const [model, effort] = groups()
    option(model!, 'Haiku').click()
    option(effort!, 'High').click()
    await nextTick()
    expect(store.threadModelId).toBe('claude-haiku-5-5')
    expect(store.threadEffort).toBe('high')
    expect(store.leadInstance?.selectedModelId).toBe('claude-opus-5-5')
    expect(AgentService.updateConversation).toHaveBeenCalledWith(1, { thread_model_name: 'claude-haiku-5-5' })
    expect(AgentService.updateConversation).toHaveBeenCalledWith(1, { thread_reasoning_effort: 'high' })
  })

  it('switches the threads off the defaults, then says they all match', async () => {
    const offEffort = { ...agent('t4', 'task', 'claude-opus-5-5'), selectedEffort: 'low' as const }
    const store = await openWith([
      agent('lead1', 'lead', 'claude-opus-5-5'),
      agent('t2', 'task', 'claude-fable-5-1'),
      agent('t3', 'task', 'claude-opus-5-5'),
      offEffort,
    ])
    const switchAll = document.body.querySelector<HTMLButtonElement>('.settings-switch')!
    expect(switchAll.textContent?.trim()).toBe('Switch 2 threads to Opus 5.5 · Medium')
    switchAll.click()
    await nextTick()
    const threads = store.instances.filter(i => i.kind === 'task')
    expect(threads.every(i => i.selectedModelId === 'claude-opus-5-5' && i.selectedEffort === 'medium')).toBe(true)
    expect(panel()?.textContent).toContain('Every thread is on Opus 5.5 · Medium.')
  })
})
