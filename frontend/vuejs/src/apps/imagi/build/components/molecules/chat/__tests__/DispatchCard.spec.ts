import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DispatchCard from '../DispatchCard.vue'
import type { AgentInstance } from '@/apps/imagi/build/types/services'

let nextId = 1

function makeTask(overrides: Partial<AgentInstance> = {}): AgentInstance {
  return {
    id: `inst-${nextId++}`,
    conversationId: nextId,
    title: 'Add a contact page',
    kind: 'task',
    parentId: 1,
    reviewStatus: 'active',
    variantGroup: '',
    hasWorktree: true,
    totalTokens: null,
    selectedModelId: 'gpt-5.6-terra',
    selectedEffort: 'medium',
    selectedFile: null,
    conversation: [],
    isProcessing: false,
    statusText: '',
    archivedAt: null,
    updatedAt: new Date().toISOString(),
    lastMessagePreview: '',
    lastAssistantSummary: '',
    brief: 'Adding a contact page so customers can reach you.',
    overview: '',
    messagesLoaded: true,
    hasUnread: false,
    queuedPrompt: null,
    ...overrides,
  }
}

const mountCard = (instance: AgentInstance | null) =>
  mount(DispatchCard, { props: { title: 'Add a contact page', instance } })

const statusOf = (wrapper: ReturnType<typeof mountCard>) =>
  wrapper.find('.dispatch-card__status').text()

/** Open the card. Closed is the resting state, so anything that reads the
 *  summary has to ask for it the way a user would. */
const opened = async (wrapper: ReturnType<typeof mountCard>) => {
  await wrapper.find('.dispatch-card__toggle').trigger('click')
  return wrapper
}

/** The summary as a reader sees it: mount, open, read. */
const summaryOf = async (instance: AgentInstance) =>
  (await opened(mountCard(instance))).find('.dispatch-card__result').text()

describe('DispatchCard', () => {
  it('reports a run that died instead of saying it is starting', async () => {
    // The bug this covers: a failed task's status had no case of its own, so
    // the card fell through to the dispatched-but-not-started branch and read
    // "Starting…" forever — for a subagent that had already stopped.
    const task = makeTask({
      reviewStatus: 'failed',
      lastMessagePreview: 'I started on the contact form and',
    })
    const wrapper = mountCard(task)

    expect(statusOf(wrapper)).toBe('Stopped before finishing')
    expect(wrapper.classes()).toContain('dispatch-card--stopped')
    // What it managed to say before it died is still worth showing.
    expect(await summaryOf(task)).toBe('I started on the contact form and')
  })

  it('shows a finished subagent its whole sign-off, every sentence of it', async () => {
    // The sign-off is a four-to-six-sentence paragraph written for the owner,
    // and this card is the only place most of them read it. Anything that
    // renders the clipped list-row preview instead drops the end of it.
    const signOff =
      'Your contact page now has a form people can fill in without leaving ' +
      'the site. It asks for a name, an email address and a message, and it ' +
      'tells someone right away if they have missed one. Your phone number ' +
      'and address sit next to the form so people can pick whichever suits ' +
      'them. The whole page reads clearly on a phone. Messages come to the ' +
      'email address in your settings, so change that if it is the wrong one.'
    const task = makeTask({
      reviewStatus: 'accepted',
      lastAssistantSummary: signOff,
      lastMessagePreview: 'Your contact page now has a form people can',
    })

    expect(statusOf(mountCard(task))).toBe('Subagent complete')
    expect(await summaryOf(task)).toBe(signOff)
  })

  it('shows a stopped run its whole last words too', async () => {
    // Same reason as a finished one: the half-finished account of what did
    // and did not land is exactly the part a clipped preview cuts off.
    const summary = await summaryOf(makeTask({
      reviewStatus: 'failed',
      lastAssistantSummary: 'I got the form onto the page, but the address block is still missing.',
      lastMessagePreview: 'I got the form onto the page, but',
    }))

    expect(summary)
      .toBe('I got the form onto the page, but the address block is still missing.')
  })

  it('never leaves a complete card with nothing under it', async () => {
    // "Subagent complete" over an empty space says nothing about the app. A
    // run that signed off with no words at all still owes the owner a line.
    for (const reviewStatus of ['accepted', 'ready'] as const) {
      expect(await summaryOf(makeTask({ reviewStatus })))
        .toBe('It finished without saying what it changed — open it to see the work.')
    }
  })

  it('still names the job it was given', () => {
    const wrapper = mountCard(makeTask({ reviewStatus: 'failed' }))
    expect(wrapper.find('.dispatch-card__job').text())
      .toBe('Adding a contact page so customers can reach you.')
  })

  it('shows a live run as working whatever its stored status', () => {
    const wrapper = mountCard(makeTask({ reviewStatus: 'failed', isProcessing: true }))
    expect(statusOf(wrapper)).toBe('Subagent working')
  })

  it('tells the owner what a working subagent is doing', async () => {
    // The state line says it is working; the overview says at what — three
    // to five plain sentences the lead wrote at dispatch, shown whole.
    const overview =
      "I'm adding a contact page with a form people can fill in without " +
      'leaving your site. It will ask for a name, an email address and a ' +
      'message, and point out anything they have missed. Your phone number ' +
      'and address will sit next to the form so people can pick whichever ' +
      'suits them.'
    const task = makeTask({ isProcessing: true, overview })
    const wrapper = await opened(mountCard(task))

    expect(statusOf(wrapper)).toBe('Subagent working')
    expect(wrapper.find('.dispatch-card__result').text()).toBe(overview)
    // The job line stays above it: the overview describes the job, it does
    // not replace its name.
    expect(wrapper.find('.dispatch-card__job').text())
      .toBe('Adding a contact page so customers can reach you.')
  })

  it('shows the overview from the moment the dispatch is staged', async () => {
    // The lead wrote it before the run fired, so there is no reason for the
    // card to have nothing behind it until then.
    const task = makeTask({
      reviewStatus: 'active',
      overview: "I'm adding a contact page with a form people can fill in.",
    })

    expect(statusOf(mountCard(task))).toBe('Subagent starting')
    expect(await summaryOf(task))
      .toBe("I'm adding a contact page with a form people can fill in.")
  })

  it('swaps the overview for the sign-off once the work lands', async () => {
    // What it was going to do is superseded by what it did — one paragraph
    // under the job, never both.
    const wrapper = await opened(mountCard(makeTask({
      reviewStatus: 'accepted',
      overview: "I'm adding a contact page with a form people can fill in.",
      lastAssistantSummary: 'Your contact page is live, with a form people can fill in.',
    })))

    expect(wrapper.find('.dispatch-card__result').text())
      .toBe('Your contact page is live, with a form people can fill in.')
    expect(wrapper.text()).not.toContain("I'm adding a contact page")
  })

  it('keeps a starting reading for a dispatch whose run has not fired', () => {
    expect(statusOf(mountCard(makeTask({ reviewStatus: 'active' }))))
      .toBe('Subagent starting')
    expect(statusOf(mountCard(null))).toBe('Subagent starting')
  })

  it('says a finished subagent already put its work in the app', () => {
    // The card is the whole of what the main thread says about this subagent,
    // so the moment it lands it has to read as landed — not as an offer the
    // user still has to accept.
    const wrapper = mountCard(makeTask({
      reviewStatus: 'accepted',
      lastAssistantSummary: 'Your contact page is live.',
    }))

    expect(statusOf(wrapper)).toBe('Subagent complete')
    expect(wrapper.classes()).toContain('dispatch-card--done')
    expect(wrapper.text()).not.toContain('waiting on you')
  })

  it('marks a parallel take as one option among several', () => {
    // 'ready' is the one state left where finished work waits on the user,
    // and only because they asked to compare versions.
    expect(statusOf(mountCard(makeTask({ reviewStatus: 'ready' }))))
      .toBe('Subagent complete — one of your options')
  })
})

describe('DispatchCard disclosure', () => {
  const OVERVIEW =
    "I'm adding a contact page with a form people can fill in without " +
    'leaving your site. It will ask for a name, an email address and a message.'

  it('starts folded, showing the state and the job and nothing else', () => {
    // Two lines answer "is it done yet?", which is what nearly every glance
    // at this card is asking. Several sentences per subagent, stacked down a
    // thread, is a wall to scroll rather than a record to read.
    const wrapper = mountCard(makeTask({ isProcessing: true, overview: OVERVIEW }))

    expect(wrapper.find('.dispatch-card__result').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('a form people can fill in')
    // What is left is still the whole answer to the question being asked.
    expect(statusOf(wrapper)).toBe('Subagent working')
    expect(wrapper.find('.dispatch-card__job').text())
      .toBe('Adding a contact page so customers can reach you.')
    // And it says there is more behind it.
    expect(wrapper.find('.dispatch-card__caret').exists()).toBe(true)
  })

  it('opens on a click and folds away again on the next one', async () => {
    const wrapper = mountCard(makeTask({ isProcessing: true, overview: OVERVIEW }))
    const toggle = wrapper.find('.dispatch-card__toggle')

    await toggle.trigger('click')
    expect(wrapper.find('.dispatch-card__result').text()).toBe(OVERVIEW)

    await toggle.trigger('click')
    expect(wrapper.find('.dispatch-card__result').exists()).toBe(false)
  })

  it('says which way it is going, out loud', async () => {
    const wrapper = mountCard(makeTask({ isProcessing: true, overview: OVERVIEW }))
    const toggle = wrapper.find('.dispatch-card__toggle')

    expect(toggle.attributes('aria-expanded')).toBe('false')
    await toggle.trigger('click')
    expect(toggle.attributes('aria-expanded')).toBe('true')
    // The paragraph it opens is the one it claims to control.
    expect(toggle.attributes('aria-controls'))
      .toBe(wrapper.find('.dispatch-card__result').attributes('id'))
  })

  it('stays open through the flip to complete', async () => {
    // Someone who opened a card to watch a job is not asking to be shut out
    // of it the moment the work lands — that is the sentence they were
    // waiting for.
    const wrapper = mountCard(makeTask({ isProcessing: true, overview: OVERVIEW }))
    await wrapper.find('.dispatch-card__toggle').trigger('click')

    await wrapper.setProps({
      instance: makeTask({
        reviewStatus: 'accepted',
        overview: OVERVIEW,
        lastAssistantSummary: 'Your contact page is live.',
      }),
    })

    expect(statusOf(wrapper)).toBe('Subagent complete')
    expect(wrapper.find('.dispatch-card__result').text()).toBe('Your contact page is live.')
  })

  it('offers nothing to open when the run has said nothing', () => {
    // A discarded card, or a dispatch that carried no overview: the state and
    // the job are the whole of it, and a caret promising more would be a lie.
    for (const instance of [
      makeTask({ reviewStatus: 'dismissed' }),
      makeTask({ isProcessing: true, overview: '' }),
    ]) {
      const wrapper = mountCard(instance)
      expect(wrapper.find('.dispatch-card__caret').exists()).toBe(false)
      expect(wrapper.find('.dispatch-card__toggle').attributes('disabled'))
        .toBeDefined()
    }
  })

  it('keeps the trip to the subagent thread on its own button', async () => {
    // One control cannot both open a panel and navigate away. Opening the
    // card is the common want, so the journey gets its own quiet mark.
    const wrapper = mountCard(makeTask({ isProcessing: true, overview: OVERVIEW }))

    await wrapper.find('.dispatch-card__open').trigger('click')

    expect(wrapper.emitted('open')).toHaveLength(1)
    // …and it does not drag the card open on its way out.
    expect(wrapper.find('.dispatch-card__result').exists()).toBe(false)
  })

  it('does not wander off to the thread when the card is opened', async () => {
    const wrapper = mountCard(makeTask({ isProcessing: true, overview: OVERVIEW }))

    await wrapper.find('.dispatch-card__toggle').trigger('click')

    expect(wrapper.emitted('open')).toBeUndefined()
  })
})
