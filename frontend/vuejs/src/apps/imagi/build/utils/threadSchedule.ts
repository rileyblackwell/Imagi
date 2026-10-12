/**
 * How a thread's place on the coordinator's schedule is said, in one place,
 * so the thread card, the coordinator's card for it and the thread's own
 * header all use the same words.
 */
import type { ScheduleThreadRef, ThreadScheduleDto } from '../types/services'

/** "A", "A and B", "A, B and C" */
export function joinNames(names: string[]): string {
  if (names.length <= 1) return names[0] || ''
  return `${names.slice(0, -1).join(', ')} and ${names[names.length - 1]}`
}

function name(ref: ScheduleThreadRef): string {
  return ref.title || 'another thread'
}

/** The threads a held thread is stuck behind: they stopped or were
 *  discarded, so they will not land until someone acts on them. */
export function stuckOn(schedule: ThreadScheduleDto | null | undefined): ScheduleThreadRef[] {
  return (schedule?.waits_on || []).filter(w => w.status === 'failed' || w.status === 'cancelled')
}

export interface ScheduleLine {
  /** 'held': waits on other work. 'blocked': waits on work that stopped.
   *  'forked': started from another thread's conversation. */
  kind: 'held' | 'blocked' | 'forked'
  icon: string
  text: string
}

/**
 * The line a card shows about how its thread was scheduled, or null when
 * there is nothing to say (an ordinary thread, running in parallel).
 */
export function scheduleLine(schedule: ThreadScheduleDto | null | undefined): ScheduleLine | null {
  if (!schedule) return null
  const waits = schedule.waits_on || []
  if (schedule.status === 'blocked') {
    const stuck = stuckOn(schedule)
    const names = joinNames((stuck.length ? stuck : waits).map(name))
    return {
      kind: 'blocked',
      icon: 'fas fa-pause',
      text: `On hold: ${names} stopped before finishing`,
    }
  }
  if (schedule.status === 'waiting' && waits.length) {
    return {
      kind: 'held',
      icon: 'fas fa-link',
      text: `Starts after ${joinNames(waits.map(name))}`,
    }
  }
  if (schedule.forked_from) {
    return {
      kind: 'forked',
      icon: 'fas fa-code-branch',
      text: `Forked from ${name(schedule.forked_from)}`,
    }
  }
  return null
}

/** The short status a held thread's card wears in the threads pane. */
export function heldStatus(schedule: ThreadScheduleDto | null | undefined): string {
  if (schedule?.status === 'blocked') {
    const stuck = stuckOn(schedule)
    return stuck.length ? `On hold: ${joinNames(stuck.map(name))} stopped` : 'On hold'
  }
  const waits = schedule?.waits_on || []
  return waits.length ? `Starts after ${joinNames(waits.map(name))}` : 'Scheduled'
}
