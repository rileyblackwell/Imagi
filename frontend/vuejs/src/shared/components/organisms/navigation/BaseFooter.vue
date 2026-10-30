<!-- The site footer, laid out as a colophon: the wordmark and one line on the
     left, three short columns on the right, and a bottom line with the
     copyright, the licence and the theme switch.

     It renders outside every page's .spotlight root, so it is its own: that
     brings the --sl-* tokens and the page floor (--sl-bg) in both themes. -->
<template>
  <footer class="spotlight border-t border-t-sl-line">
    <div class="max-w-7xl mx-auto px-6 pt-14 sm:px-8 lg:px-12 lg:pt-16">
      <div class="grid gap-10 pb-12 min-[900px]:grid-cols-[1.15fr_2fr] min-[900px]:gap-12">
        <div class="grid gap-[0.875rem] [align-content:start] justify-items-start">
          <ImagiLogo size="lg" />
          <p class="m-0 max-w-[30ch] text-[15.5px] leading-[1.55] text-sl-muted">Build and run your business from one place.</p>
        </div>

        <nav class="grid grid-cols-2 gap-8 min-[560px]:grid-cols-3" aria-label="Footer">
          <div v-for="col in columns" :key="col.title">
            <h2 class="m-0 mb-[0.875rem] text-[11.5px] font-semibold tracking-[0.16em] uppercase text-sl-muted">{{ col.title }}</h2>
            <ul class="m-0 p-0 list-none grid gap-[0.7rem]">
              <li v-for="link in col.links" :key="link.label">
                <router-link :to="link.to" :class="linkClass">{{ link.label }}</router-link>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      <div class="flex flex-wrap items-center justify-between gap-y-3 gap-x-6 pt-5 pb-[1.6rem] border-t border-t-sl-line">
        <p class="m-0 text-[13.5px] text-sl-muted">&copy; {{ currentYear }} Imagi. MIT licensed.</p>
        <ThemeToggle />
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ThemeToggle } from '@/shared/components/atoms'
import { ImagiLogo } from '@/shared/components/molecules'

const currentYear = computed(() => new Date().getFullYear())

const linkClass =
  'text-[14.5px] text-sl-text rounded-[2px] [transition:color_0.2s_cubic-bezier(0.22,1,0.36,1)] hover:text-sl-muted'

const columns: { title: string; links: { label: string; to: string }[] }[] = [
  {
    title: 'Product',
    links: [
      { label: 'Pricing', to: '/payments/pricing' },
      { label: 'Docs', to: '/docs' },
    ],
  },
  {
    title: 'Company',
    links: [
      { label: 'About', to: '/about' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { label: 'Privacy Policy', to: '/privacy' },
      { label: 'Terms of Service', to: '/terms' },
    ],
  },
]
</script>
