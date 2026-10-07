import { describe, it, expect } from 'vitest'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const css = readFileSync(resolve(__dirname, '../spotlight.css'), 'utf8')

// The declarations inside the first `<selector> {` block
function tokens(selector: string): Set<string> {
  const start = css.indexOf(`${selector} {`)
  const body = css.slice(start, css.indexOf('\n}', start))
  return new Set([...body.matchAll(/^\s*(--[\w-]+):/gm)].map((m) => m[1]))
}

// Tokens that are the same in both themes by design
const SHARED = ['--sl-grad', '--sl-on-accent', '--sl-font-display', '--sl-font-body']

describe('Spotlight palettes', () => {
  it('gives every colour token a dark-theme value too', () => {
    const light = tokens('.spotlight')
    const dark = tokens('.dark .spotlight')
    const missing = [...light].filter((t) => !dark.has(t) && !SHARED.includes(t))
    expect(missing).toEqual([])
  })
})
