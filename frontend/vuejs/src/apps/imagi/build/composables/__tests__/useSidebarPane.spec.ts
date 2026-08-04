import { describe, it, expect, beforeEach } from 'vitest'
import { useSidebarPane } from '../useSidebarPane'

describe('useSidebarPane', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('the masthead switch', () => {
    // One model at every width: the pane the sidebar renders is named by one
    // ref, and the switch pill is its only writer. The regression this replaces
    // came from having a second, mobile-only view state that a writer could
    // forget — pressing the pill then changed the pane on one layout and did
    // nothing at all on the other.
    it('moves the rendered pane', () => {
      const { setSidebarView, sidebarView } = useSidebarPane()

      expect(sidebarView.value).toBe('chat')
      setSidebarView('manager')
      expect(sidebarView.value).toBe('manager')
      setSidebarView('chat')
      expect(sidebarView.value).toBe('chat')
    })
  })

  describe('the preview', () => {
    it('is reached by collapsing the sidebar, not by naming a third view', () => {
      const { showPreview } = useSidebarPane()
      const collapsed: boolean[] = []

      showPreview(v => collapsed.push(v))
      expect(collapsed).toEqual([true])
    })

    it('leaves the pane underneath alone, so coming back lands where you left', () => {
      const { setSidebarView, showPreview, sidebarView } = useSidebarPane()

      setSidebarView('manager')
      showPreview(() => {})
      expect(sidebarView.value).toBe('manager')
    })

    it('opens the sidebar and names the pane in one act on the way back', () => {
      // Either half alone lands somewhere the user didn't ask for: naming the
      // pane without opening leaves the preview up, opening without naming
      // reopens on whatever pane happened to be behind it.
      const { setSidebarView, showPane, sidebarView } = useSidebarPane()
      const collapsed: boolean[] = []

      setSidebarView('manager')
      showPane('chat', v => collapsed.push(v))

      expect(sidebarView.value).toBe('chat')
      expect(collapsed).toEqual([false])
    })
  })

  describe('persistence', () => {
    it('reopens on the pane the user left it on', () => {
      const first = useSidebarPane()
      first.setSidebarView('manager')

      const reopened = useSidebarPane()
      expect(reopened.sidebarView.value).toBe('manager')
    })

    it('reopens on the chat pane when nothing was stored', () => {
      expect(useSidebarPane().sidebarView.value).toBe('chat')
    })

    it('remembers a return from the preview, not the preview itself', () => {
      // The preview is the layout's collapsed state, persisted under the
      // layout's own key — this composable must not shadow it with a pane name.
      const { showPane } = useSidebarPane()
      showPane('manager', () => {})

      expect(useSidebarPane().sidebarView.value).toBe('manager')
    })
  })
})
