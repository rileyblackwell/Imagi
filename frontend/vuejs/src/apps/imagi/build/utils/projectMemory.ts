/**
 * Reading the project memory document for the memory view.
 *
 * The memory is markdown with a few fixed `## ` sections, each a list of
 * one-line facts (services/project_memory.py on the backend). The view shows
 * it section by section; anything the user wrote outside a list still shows,
 * as a plain line.
 */
import type { ProjectMemoryChange } from '../types/services'

export interface MemorySection {
  title: string
  lines: string[]
}

const HEADING = /^##\s+(.*\S)\s*$/
const BULLET = /^\s*(?:[-*+]|\d+[.)])\s+/

/** The document as sections of lines, plus anything above the first heading. */
export function parseMemory(content: string): { preamble: string[]; sections: MemorySection[] } {
  const preamble: string[] = []
  const sections: MemorySection[] = []
  for (const raw of (content || '').split('\n')) {
    const heading = raw.match(HEADING)
    if (heading) {
      sections.push({ title: heading[1] ?? '', lines: [] })
      continue
    }
    const text = raw.replace(BULLET, '').trim()
    if (!text) continue
    const current = sections[sections.length - 1]
    if (current) current.lines.push(text)
    else if (!/^#\s/.test(raw)) preamble.push(text)
  }
  return { preamble, sections }
}

/** How many facts the memory holds. */
export function memoryLineCount(content: string): number {
  const { preamble, sections } = parseMemory(content)
  return preamble.length + sections.reduce((n, s) => n + s.lines.length, 0)
}

/** Who made a change, in a few words. */
export function changeByline(change: ProjectMemoryChange): string {
  const title = change.source?.title
  switch (change.author) {
    case 'user':
      return 'You'
    case 'thread':
      return title ? `Thread · ${title}` : 'A thread'
    case 'coordinator':
      return 'Coordinator'
    default:
      if (change.source?.kind === 'task') return title ? `Saved from thread · ${title}` : 'Saved from a thread'
      return 'Saved from your chat'
  }
}

/** "just now", "5 min ago", "3 h ago", then a date. */
export function timeAgo(iso: string | null | undefined, now: number = Date.now()): string {
  if (!iso) return ''
  const then = new Date(iso).getTime()
  if (Number.isNaN(then)) return ''
  const minutes = Math.floor((now - then) / 60000)
  if (minutes < 1) return 'just now'
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours} h ago`
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}
