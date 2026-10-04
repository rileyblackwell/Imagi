import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'

const push = vi.fn()
const auth = { isAuthenticated: false }
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))
vi.mock('@/shared/stores/auth', () => ({ useAuthStore: () => auth }))

import IdeaPrompt from '../IdeaPrompt.vue'
import { peekPendingIdea, savePendingIdea } from '@/apps/home/utils/pendingIdea'

/**
 * The prompt replaces the home page's "Start building" button, so it has to do
 * everything the button did — get the visitor to the projects page, through
 * sign-in if needed — and also carry what they typed.
 */
describe('IdeaPrompt', () => {
  beforeEach(() => {
    sessionStorage.clear()
    push.mockClear()
    auth.isAuthenticated = false
  })

  it('sends signed-out visitors to sign in, then back to the projects page, with the idea kept', async () => {
    const wrapper = mount(IdeaPrompt)
    await wrapper.find('textarea').setValue('A booking site for my dog-grooming studio')
    await wrapper.find('form').trigger('submit')
    expect(peekPendingIdea()).toBe('A booking site for my dog-grooming studio')
    expect(push).toHaveBeenCalledWith({ name: 'login', query: { redirect: '/imagi/projects' } })
  })

  it('sends signed-in visitors straight to the projects page', async () => {
    auth.isAuthenticated = true
    const wrapper = mount(IdeaPrompt)
    await wrapper.find('textarea').setValue('An online shop for hot sauce')
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter' })
    expect(push).toHaveBeenCalledWith({ name: 'projects' })
  })

  it('still navigates when submitted empty, like the old button', async () => {
    savePendingIdea('stale idea')
    const wrapper = mount(IdeaPrompt)
    await wrapper.find('form').trigger('submit')
    expect(peekPendingIdea()).toBe('')
    expect(push).toHaveBeenCalledTimes(1)
  })

  it('does not submit on Shift+Enter', async () => {
    const wrapper = mount(IdeaPrompt)
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter', shiftKey: true })
    expect(push).not.toHaveBeenCalled()
  })

  it('fills the box from a suggestion and reports engagement', async () => {
    const wrapper = mount(IdeaPrompt, {
      props: { suggestions: [{ label: 'Online store', text: 'An online store that sells ' }] }
    })
    await wrapper.find('.idea__chip').trigger('click')
    expect((wrapper.find('textarea').element as HTMLTextAreaElement).value).toBe('An online store that sells ')
    expect(wrapper.emitted('engage')).toBeTruthy()
  })

  it('restores an idea from earlier in the session only when asked to', async () => {
    savePendingIdea('A subscription box for tea')
    const plain = mount(IdeaPrompt)
    const restoring = mount(IdeaPrompt, { props: { restore: true } })
    await flushPromises()
    expect((plain.find('textarea').element as HTMLTextAreaElement).value).toBe('')
    expect((restoring.find('textarea').element as HTMLTextAreaElement).value).toBe('A subscription box for tea')
    expect(restoring.emitted('engage')).toBeTruthy()
  })
})
