/**
 * When a project was last worked on, in the words a person would use:
 * "Just now", "12 minutes ago", "Yesterday", "3 days ago", then a date.
 * Returns '' for a missing or unparseable timestamp, so the list can drop
 * the label rather than print "Invalid Date".
 */
export function updatedLabel(iso: string | undefined | null, now: Date = new Date()): string {
  if (!iso) return ''
  const then = new Date(iso)
  if (Number.isNaN(then.getTime())) return ''

  const mins = Math.floor((now.getTime() - then.getTime()) / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins} minute${mins === 1 ? '' : 's'} ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} hour${hours === 1 ? '' : 's'} ago`
  const days = Math.floor(hours / 24)
  if (days < 2) return 'Yesterday'
  if (days < 7) return `${days} days ago`

  return then.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    ...(then.getFullYear() === now.getFullYear() ? {} : { year: 'numeric' }),
  })
}
