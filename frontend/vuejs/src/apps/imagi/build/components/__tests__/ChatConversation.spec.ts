import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChatConversation from '../organisms/chat/ChatConversation.vue'
import type { AIMessage } from '@/apps/imagi/build/types/services'

const user = (content: string): AIMessage => ({
  role: 'user', content, timestamp: '2026-01-01T00:00:00Z', id: 'u1',
})
const assistant = (content: string): AIMessage => ({
  role: 'assistant', content, timestamp: '2026-01-01T00:00:01Z', id: 'a1',
})

const indicatorText = (wrapper: ReturnType<typeof mount>) => {
  const indicator = wrapper.find('.typing-indicator')
  return indicator.exists() ? indicator.element.parentElement?.textContent?.trim() : null
}

describe('ChatConversation activity indicator', () => {
  const mountWith = (props: object) =>
    mount(ChatConversation, { props: { messages: [user('hi')], ...props } })

  it('shows the status while the agent has not started replying', () => {
    const wrapper = mountWith({ isProcessing: true, statusText: 'Thinking…' })
    expect(indicatorText(wrapper)).toBe('Thinking…')
  })

  it('falls back to a generic label without a status', () => {
    const wrapper = mountWith({ isProcessing: true })
    expect(indicatorText(wrapper)).toBe('Working…')
  })

  it('hides while the reply is streaming in', () => {
    // The growing assistant message already shows progress; a second
    // indicator under it would just dangle.
    const wrapper = mountWith({
      isProcessing: true,
      statusText: '',
      messages: [user('hi'), assistant('partial reply')],
    })
    expect(indicatorText(wrapper)).toBeNull()
  })

  it('returns with tool activity after text has streamed', () => {
    const wrapper = mountWith({
      isProcessing: true,
      statusText: 'Editing project files…',
      messages: [user('hi'), assistant('working on it')],
    })
    expect(indicatorText(wrapper)).toBe('Editing project files…')
  })

  it('hides when the run is over', () => {
    const wrapper = mountWith({
      isProcessing: false,
      messages: [user('hi'), assistant('done')],
    })
    expect(indicatorText(wrapper)).toBeNull()
  })
})
