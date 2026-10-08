import { describe, it, expect, beforeEach, vi } from 'vitest'
import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import type { CheckInDto } from '@/apps/imagi/build/types/services'

const showNotification = vi.hoisted(() => vi.fn())
vi.mock('@/shared/composables/useNotification', () => ({
  useNotification: () => ({ showNotification }),
}))
vi.mock('@/apps/imagi/build/services/agentService', () => ({ AgentService: {} }))

import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import {
  useThreadNotifications,
  describeWaitingCheckIn,
} from '../useThreadNotifications'

function checkIn(id: number, kind: CheckInDto['kind'], goal = 'Building a booking page'): CheckInDto {
  return {
    id,
    kind,
    body: '',
    status: 'pending',
    created_at: '',
    resolved_at: null,
    project_id: 1,
    lead_id: 1,
    task: {
      id: 100 + id, title: '', goal, kind: 'task', review_status: 'input',
      variant_group: '', has_worktree: true, is_running: false,
    },
  }
}

const Host = defineComponent({
  setup() {
    useThreadNotifications()
    return () => null
  },
})

describe('useThreadNotifications', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    showNotification.mockReset()
    document.title = 'Imagi'
  })

  it('stays quiet about what was already waiting when the workspace opened', async () => {
    const store = useAgentStore()
    mount(Host)
    store.checkIns = [checkIn(1, 'question')]
    store.checkInsLoaded = true
    await nextTick()

    expect(showNotification).not.toHaveBeenCalled()
  })

  it('announces a thread that starts waiting after the first load', async () => {
    const store = useAgentStore()
    mount(Host)
    store.checkInsLoaded = true
    await nextTick()

    store.checkIns = [checkIn(2, 'done'), checkIn(3, 'question')]
    await nextTick()

    expect(showNotification).toHaveBeenCalledTimes(1)
    expect(showNotification.mock.calls[0]![0].message).toContain('“Building a booking page” needs your answer')

    // The next poll returns the same queue: nothing new to say.
    store.checkIns = [...store.checkIns]
    await nextTick()
    expect(showNotification).toHaveBeenCalledTimes(1)
  })

  it('puts the waiting count in the tab title and takes it out again', async () => {
    const store = useAgentStore()
    const wrapper = mount(Host)
    store.checkIns = [checkIn(4, 'question'), checkIn(5, 'error'), checkIn(6, 'done')]
    await nextTick()
    expect(document.title).toBe('(2) Imagi')

    store.checkIns = []
    await nextTick()
    expect(document.title).toBe('Imagi')

    store.checkIns = [checkIn(7, 'question')]
    await nextTick()
    wrapper.unmount()
    expect(document.title).toBe('Imagi')
  })

  it('words each kind of waiting', () => {
    expect(describeWaitingCheckIn(checkIn(1, 'ready'))).toContain('versions ready')
    expect(describeWaitingCheckIn(checkIn(1, 'error'))).toContain('stopped before finishing')
  })
})
