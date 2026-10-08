import { onBeforeUnmount, watch } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { useNotification } from '@/shared/composables/useNotification'
import type { CheckInDto } from '../types/services'

/** What the toast says when a thread starts waiting on the user. */
export function describeWaitingCheckIn(checkIn: CheckInDto): string {
  const name = checkIn.task.goal || checkIn.task.title || 'A thread'
  switch (checkIn.kind) {
    case 'question':
      return `“${name}” needs your answer. Reply in the coordinator chat or in the thread.`
    case 'ready':
      return `“${name}” has versions ready for you to pick from.`
    case 'error':
      return `“${name}” stopped before finishing.`
    default:
      return `“${name}” finished.`
  }
}

/**
 * Tell the user when a thread starts waiting on them.
 *
 * The coordinator chat already queues every check-in above its composer, but
 * that is only seen by someone looking at it. So a thread that newly asks a
 * question, has takes to pick from, or stops also raises a toast wherever the
 * user is in the workspace, and the browser tab's title carries the count of
 * threads waiting, so it reads from another tab too.
 *
 * Only arrivals after the queue's first load count as news: what was already
 * waiting when the workspace opened is on screen in the coordinator chat.
 */
export function useThreadNotifications() {
  const store = useAgentStore()
  const { showNotification } = useNotification()
  const announced = new Set<number>()
  const baseTitle = typeof document !== 'undefined' ? document.title : ''

  const stopArrivals = watch(
    () => [store.checkInsLoaded, store.waitingCheckIns.map(c => c.id).join(',')] as const,
    ([loaded], previous) => {
      const wasLoaded = previous?.[0] ?? false
      for (const checkIn of store.waitingCheckIns) {
        if (announced.has(checkIn.id)) continue
        announced.add(checkIn.id)
        // The first load primes the set; it announces nothing.
        if (!loaded || !wasLoaded) continue
        // Already looking at that very thread: its transcript says it.
        const opened = store.openedThread ?? store.activeInstance
        if (opened?.conversationId === checkIn.task.id) continue
        showNotification({
          type: checkIn.kind === 'error' ? 'warning' : 'info',
          message: describeWaitingCheckIn(checkIn),
          duration: 8000,
        })
      }
    },
    { immediate: true }
  )

  const stopTitle = watch(
    () => store.waitingCheckIns.length,
    count => {
      if (typeof document === 'undefined') return
      document.title = count > 0 ? `(${count}) ${baseTitle}` : baseTitle
    },
    { immediate: true }
  )

  onBeforeUnmount(() => {
    stopArrivals()
    stopTitle()
    if (typeof document !== 'undefined') document.title = baseTitle
  })
}
