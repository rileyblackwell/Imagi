import type { Directive } from 'vue'

/**
 * v-reveal — fades and lifts an element into view the first time it enters
 * the viewport. Usage: `v-reveal` or `v-reveal="{ delay: 120 }"` (ms).
 * Respects prefers-reduced-motion by leaving the element fully visible.
 * The transition styles live in Home.vue's unscoped style block
 * (.reveal-init / .is-revealed).
 */

interface RevealOptions {
  delay?: number
}

let observer: IntersectionObserver | null = null

// Once the reveal transition has played, strip the transition override and
// inline delay so later transitions (e.g. card hover lifts) aren't lagged
// by the stagger delay.
function finishReveal(el: HTMLElement) {
  // transitionDelay is always set by this directive as "<n>ms"
  const delay = parseFloat(el.style.transitionDelay) || 0
  window.setTimeout(() => {
    el.classList.remove('reveal-init', 'is-revealed')
    el.style.transitionDelay = ''
  }, delay + 850)
}

function getObserver(): IntersectionObserver {
  if (!observer) {
    observer = new IntersectionObserver(
      entries => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed')
            finishReveal(entry.target as HTMLElement)
            observer?.unobserve(entry.target)
          }
        }
      },
      { threshold: 0, rootMargin: '0px 0px -60px 0px' }
    )
  }
  return observer
}

const reveal: Directive<HTMLElement, RevealOptions | undefined> = {
  mounted(el, binding) {
    if (
      typeof window === 'undefined' ||
      !('IntersectionObserver' in window) ||
      window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ) {
      return
    }
    el.classList.add('reveal-init')
    const delay = binding.value?.delay
    if (delay) {
      el.style.transitionDelay = `${delay}ms`
    }
    getObserver().observe(el)
  },
  unmounted(el) {
    observer?.unobserve(el)
  }
}

export default reveal
