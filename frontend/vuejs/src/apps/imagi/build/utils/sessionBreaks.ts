/**
 * Session breaks in a chat transcript: where a sitting starts, and how its
 * start time is written. Used by the coordinator chat and by threads.
 *
 * A sitting starts at the first message, and again after any quiet spell of
 * SESSION_GAP_MS or more between two messages, so coming back to the
 * workspace later reads as a new block with its own start time.
 */

/** How long a quiet spell has to be before the next message starts a new
 *  sitting. */
export const SESSION_GAP_MS = 30 * 60 * 1000

type Stamp = string | number | undefined

function timeOf(timestamp: Stamp): number | null {
  if (timestamp === undefined || timestamp === '') return null
  const t = new Date(timestamp).getTime()
  return Number.isNaN(t) ? null : t
}

/** Indexes of the messages that open a sitting. A message without a readable
 *  time never opens one, and does not reset the gap. */
export function sessionStartIndexes(
  messages: ReadonlyArray<{ timestamp?: string | number }>,
  gapMs: number = SESSION_GAP_MS
): Set<number> {
  const starts = new Set<number>()
  let previous: number | null = null
  messages.forEach((message, index) => {
    const t = timeOf(message.timestamp)
    if (t === null) return
    if (previous === null || t - previous >= gapMs) starts.add(index)
    previous = t
  })
  return starts
}

function startOfDay(d: Date): number {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime()
}

/**
 * A sitting's start, as the separator says it: "Today · 3:42 PM",
 * "Yesterday · 9:05 AM", "Monday · 4:15 PM" within the last week, then
 * "Oct 3 · 4:15 PM" (with the year once it is not this year).
 */
export function formatSessionStart(timestamp: Stamp, now: Date = new Date()): string {
  const t = timeOf(timestamp)
  if (t === null) return ''
  const date = new Date(t)
  const time = date.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })
  const days = Math.round((startOfDay(now) - startOfDay(date)) / 86_400_000)
  let day: string
  if (days <= 0) day = 'Today'
  else if (days === 1) day = 'Yesterday'
  else if (days < 7) day = date.toLocaleDateString(undefined, { weekday: 'long' })
  else if (date.getFullYear() === now.getFullYear()) {
    day = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  } else {
    day = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
  }
  return `${day} · ${time}`
}

/** The same moment as an ISO string, for a <time datetime>. */
export function sessionIso(timestamp: Stamp): string {
  const t = timeOf(timestamp)
  return t === null ? '' : new Date(t).toISOString()
}
