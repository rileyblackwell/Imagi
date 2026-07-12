/**
 * On-device viewport diagnostics for the intermittent iPad render glitch.
 *
 * Enable by visiting any page with ?debug=1 (persists via localStorage);
 * disable with ?debug=0. Renders a small always-on-top readout of the
 * numbers that distinguish the possible failure modes:
 *
 * - scrollY stuck > 0            → a real scroll-position bug
 * - visualViewport offset != 0   → layout/visual viewport desync (WebKit)
 * - all numbers normal while the
 *   screen looks wrong           → stale compositor tiles (pure paint bug)
 *
 * Deliberately framework-free so it works even if the app wedges.
 */
export function initViewportDebug(): void {
  const params = new URLSearchParams(window.location.search)
  const flag = params.get('debug')
  if (flag === '1') localStorage.setItem('imagi-debug', '1')
  if (flag === '0') localStorage.removeItem('imagi-debug')
  if (localStorage.getItem('imagi-debug') !== '1') return

  const box = document.createElement('div')
  box.id = 'imagi-debug'
  box.style.cssText = [
    'position:fixed', 'left:8px', 'bottom:8px', 'z-index:2147483647',
    'font:11px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace',
    'background:rgba(0,0,0,0.82)', 'color:#7CFC9A', 'padding:8px 10px',
    'border-radius:8px', 'pointer-events:none', 'white-space:pre',
    'max-width:92vw', 'overflow:hidden',
  ].join(';')
  const el = document.createElement('div')
  // "force top" probe: reports whether programmatic scrolling can beat a
  // stuck scroll floor (gesture scrolling and JS scrolling can differ when
  // WebKit's scroll bounds are corrupted).
  const btn = document.createElement('button')
  btn.textContent = '⤒ force top'
  btn.style.cssText =
    'pointer-events:auto;margin-top:6px;font:inherit;color:#0a0a0a;background:#7CFC9A;border:0;border-radius:6px;padding:4px 8px'
  btn.addEventListener('click', () => {
    window.scrollTo(0, 0)
    setTimeout(() => {
      btn.textContent = window.scrollY === 0 ? '⤒ force top — ok' : `⤒ force top — stuck at ${Math.round(window.scrollY)}`
    }, 350)
  })
  box.appendChild(el)
  box.appendChild(btn)
  document.body.appendChild(box)

  const fmt = (n: number | undefined) => (n === undefined ? '?' : Math.round(n * 10) / 10)

  const render = () => {
    const vv = window.visualViewport
    const nav = document.querySelector('nav')
    const h1 = document.querySelector('h1')
    const doc = document.scrollingElement
    el.textContent = [
      `build  ${document.documentElement.dataset.build ?? '?'}`,
      `scrollY ${fmt(window.scrollY)}  docTop ${fmt(doc?.scrollTop)}`,
      `inner  ${window.innerWidth}x${window.innerHeight}  docH ${fmt(doc?.scrollHeight)}`,
      `vv     off ${fmt(vv?.offsetTop)},${fmt(vv?.offsetLeft)}  h ${fmt(vv?.height)}  scale ${fmt(vv?.scale)}`,
      `nav    top ${fmt(nav?.getBoundingClientRect().top)}  h1 top ${fmt(h1?.getBoundingClientRect().top)}`,
    ].join('\n')
  }

  let scheduled = false
  const schedule = () => {
    if (scheduled) return
    scheduled = true
    requestAnimationFrame(() => {
      scheduled = false
      render()
    })
  }

  window.addEventListener('scroll', schedule, { passive: true })
  window.addEventListener('resize', schedule)
  window.visualViewport?.addEventListener('resize', schedule)
  window.visualViewport?.addEventListener('scroll', schedule)
  document.addEventListener('visibilitychange', schedule)
  setInterval(schedule, 1000)
  render()
}
