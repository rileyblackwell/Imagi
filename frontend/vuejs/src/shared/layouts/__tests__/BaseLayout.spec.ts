import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseLayout from '../BaseLayout.vue'

/**
 * Two page shapes, and confusing them is a real bug rather than a cosmetic
 * one.
 *
 * The builder workspace puts its chrome in three different places: the navbar
 * and the agent sidebar are `fixed`, but the browser pane's toolbar — the file
 * selector above the preview — sits in normal document flow. So the moment the
 * page gains a single scrollable pixel, that toolbar slides up under the navbar
 * while the other two stay exactly where they are. The fix is to leave the app
 * shell no scrollable pixel to find: it is taken out of flow, and it builds no
 * scroll container.
 *
 * Ordinary pages must keep scrolling normally, which is the other half of the
 * contract and the easier half to break by accident.
 */
describe('BaseLayout', () => {
  const frameOf = (appShell: boolean) => {
    const wrapper = mount(BaseLayout, {
      props: { appShell },
      slots: { default: '<p>content</p>' },
    })
    const root = wrapper.find('div')
    return { root, inner: wrapper.find('.app-scroll'), wrapper }
  }

  describe('app shell', () => {
    it('takes the page out of flow so the document has nothing to scroll', () => {
      const { root } = frameOf(true)
      // Out of flow, pinned to the top, and sized to the *dynamic* viewport —
      // h-dvh rather than h-screen, so mobile browser chrome cannot leave a
      // strip of overshoot behind.
      expect(root.classes()).toContain('fixed')
      expect(root.classes()).toContain('top-0')
      expect(root.classes()).toContain('h-dvh')
      expect(root.classes()).not.toContain('min-h-dvh')
    })

    it('refuses to chain a gesture out to the page behind it', () => {
      expect(frameOf(true).root.classes()).toContain('overscroll-none')
    })

    it('builds no scroll container around the content', () => {
      const { root, inner } = frameOf(true)
      // Both boxes carry the clip treatment (see the component's styles for
      // why clip and not hidden), and neither is a scroller.
      expect(root.classes()).toContain('app-shell-frame')
      expect(inner.classes()).toContain('app-shell-frame')
      expect(inner.classes()).not.toContain('overflow-auto')
    })
  })

  describe('ordinary pages', () => {
    it('still scrolls, and does so on the document', () => {
      const { root, inner } = frameOf(false)
      expect(root.classes()).toContain('min-h-dvh')
      expect(root.classes()).not.toContain('fixed')
      expect(inner.classes()).toContain('overflow-auto')
      expect(inner.classes()).not.toContain('app-shell-frame')
    })

    it('is the default, so no caller has to opt out of the app shell', () => {
      const wrapper = mount(BaseLayout, { slots: { default: '<p>content</p>' } })
      expect(wrapper.find('div').classes()).toContain('min-h-dvh')
    })
  })

  it('renders what it is given, either way', () => {
    expect(frameOf(true).wrapper.text()).toContain('content')
    expect(frameOf(false).wrapper.text()).toContain('content')
  })
})
