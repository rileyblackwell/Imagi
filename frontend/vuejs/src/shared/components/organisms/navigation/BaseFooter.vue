<!-- The site footer, laid out as a colophon: the wordmark and one line on the
     left, three short columns on the right, and a bottom line with the
     copyright, the licence and the theme switch.

     It renders outside every page's .spotlight root, so it is its own: that
     brings the --sl-* tokens and the page floor (--sl-bg) in both themes. -->
<template>
  <footer class="spotlight site-footer">
    <div class="site-footer__inner">
      <div class="site-footer__top">
        <div class="site-footer__brand">
          <ImagiLogo size="lg" />
          <p>Build and run your business from one place.</p>
        </div>

        <nav class="site-footer__cols" aria-label="Footer">
          <div v-for="col in columns" :key="col.title" class="site-footer__col">
            <h2>{{ col.title }}</h2>
            <ul>
              <li v-for="link in col.links" :key="link.label">
                <router-link :to="link.to">{{ link.label }}</router-link>
              </li>
            </ul>
          </div>
        </nav>
      </div>

      <div class="site-footer__bottom">
        <p>&copy; {{ currentYear }} Imagi. MIT licensed.</p>
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

<style scoped>
.site-footer {
  border-top: 1px solid var(--sl-line);
}

.site-footer__inner {
  max-width: 80rem;
  margin: 0 auto;
  padding: 3.5rem 1.5rem 0;
}

@media (min-width: 640px) {
  .site-footer__inner {
    padding-inline: 2rem;
  }
}

@media (min-width: 1024px) {
  .site-footer__inner {
    padding: 4rem 3rem 0;
  }
}

.site-footer__top {
  display: grid;
  gap: 2.5rem;
  padding-bottom: 3rem;
}

@media (min-width: 900px) {
  .site-footer__top {
    grid-template-columns: 1.15fr 2fr;
    gap: 3rem;
  }
}

.site-footer__brand {
  display: grid;
  gap: 0.875rem;
  align-content: start;
  justify-items: start;
}

.site-footer__brand p {
  margin: 0;
  max-width: 30ch;
  font-size: 15.5px;
  line-height: 1.55;
  color: var(--sl-muted);
}

.site-footer__cols {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 2rem;
}

@media (min-width: 560px) {
  .site-footer__cols {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.site-footer__col h2 {
  margin: 0 0 0.875rem;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.site-footer__col ul {
  margin: 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 0.7rem;
}

.site-footer__col a {
  font-size: 14.5px;
  color: var(--sl-text);
  border-radius: 2px;
  transition: color 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.site-footer__col a:hover {
  color: var(--sl-muted);
}

.site-footer__bottom {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1.5rem;
  padding: 1.25rem 0 1.6rem;
  border-top: 1px solid var(--sl-line);
}

.site-footer__bottom p {
  margin: 0;
  font-size: 13.5px;
  color: var(--sl-muted);
}
</style>
