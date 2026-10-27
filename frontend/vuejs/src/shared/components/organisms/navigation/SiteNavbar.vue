<!-- The site's main top bar. Used by every page that is not sign-in or checkout
     — home, docs, pricing, the project hub, and the three tool workspaces — via
     DefaultLayout.

     Visitors get the wordmark and one ink Sign in pill, at every width.
     Signed in, the Product menu (Imagi, to the projects page) and Pricing sit
     centred in the bar, and a quiet Sign out sits on the right. Docs and About
     are in the footer. The page you are on is set in full ink. The coral light
     stays with the page. Below md the signed-in links fold into a Menu sheet.

     The bar sits outside every page's .spotlight root, so the link groups and
     the sheet carry their own `.spotlight` for the --sl-* tokens, as the
     Product menu's panel does. -->
<template>
  <BaseNavbar fluid v-bind="$attrs">
    <!-- Passed through for layouts that pin a control before the wordmark
         (the docs' sidebar toggle) -->
    <template #left-leading>
      <slot name="left-leading"></slot>
    </template>

    <!-- Product and Pricing are for the signed-in, centred in the bar -->
    <template #center>
      <div v-if="isAuthenticated" class="spotlight site-nav-group hidden md:flex items-center gap-1">
        <SiteNavbarDropdown v-model="isProductsMenuOpen" :active="isActive('/imagi')">
          Product

          <template #menu>
            <router-link
              :to="{ name: 'builder' }"
              class="nav-menu-item group"
              @click="isProductsMenuOpen = false"
            >
              <span class="min-w-0 flex-1">
                <span class="nav-menu-item__title">Imagi</span>
                <span class="nav-menu-item__desc">Build and <em class="sl-run">run</em> your business</span>
              </span>
              <i class="fas fa-arrow-right nav-menu-item__arrow" aria-hidden="true"></i>
            </router-link>
          </template>
        </SiteNavbarDropdown>

        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          class="site-nav-link"
          :class="{ 'is-active': isActive(link.match) }"
          :aria-current="isActive(link.match) ? 'page' : undefined"
        >
          {{ link.label }}
        </router-link>
      </div>
    </template>

    <template #right>
      <div class="spotlight site-nav-group flex items-center gap-3">
        <template v-if="isAuthenticated">
          <div class="hidden md:flex">
            <button type="button" class="site-nav-link" @click="handleLogout">Sign out</button>
          </div>

          <button
            type="button"
            class="site-nav-menu-btn md:hidden"
            :aria-expanded="isMobileMenuOpen ? 'true' : 'false'"
            aria-controls="site-nav-sheet"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
          >
            <i class="fas" :class="isMobileMenuOpen ? 'fa-xmark' : 'fa-bars'" aria-hidden="true"></i>
            {{ isMobileMenuOpen ? 'Close' : 'Menu' }}
          </button>
        </template>
        <!-- Visitors have one thing to do here, so it is the bar's one button -->
        <router-link v-else to="/auth/signin" class="site-nav-cta">Sign in</router-link>
      </div>
    </template>
  </BaseNavbar>

  <!-- Phone menu, signed in only: a sheet hung under the bar over a soft scrim -->
  <transition name="site-sheet">
    <div v-if="isAuthenticated && isMobileMenuOpen" class="md:hidden">
      <div class="site-sheet-scrim" @click="isMobileMenuOpen = false"></div>
      <div id="site-nav-sheet" class="spotlight site-sheet">
        <div class="site-sheet__group">
          <p class="site-sheet__label">Product</p>
          <router-link
            :to="{ name: 'builder' }"
            class="site-sheet__link"
            :class="{ 'is-active': isActive('/imagi') }"
          >
            Imagi
          </router-link>
          <router-link
            to="/payments/pricing"
            class="site-sheet__link"
            :class="{ 'is-active': isActive('/payments') }"
          >
            Pricing
          </router-link>
        </div>

        <div class="site-sheet__actions">
          <button type="button" class="site-sheet__btn" @click="handleLogout">Sign out</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import { useAuth } from '@/apps/auth'
import BaseNavbar from './BaseNavbar.vue'
import SiteNavbarDropdown from './SiteNavbarDropdown.vue'

// Two roots (the bar and the phone sheet), so a layout's classes go to the bar
defineOptions({ name: 'SiteNavbar', inheritAttrs: false })

// Passed through to the bar, for layouts that pin a control before the
// wordmark (the docs' sidebar toggle)
defineSlots<{ 'left-leading'?: () => unknown }>()

// `match` is the path prefix that marks the link as the current page, so
// every page under it (/payments/...) still lights the link. Docs and About
// live in the footer.
const links = [
  { label: 'Pricing', to: '/payments/pricing', match: '/payments' }
]

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { logout } = useAuth()
const isProductsMenuOpen = ref(false)
const isMobileMenuOpen = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)

const isActive = (prefix: string) => {
  const path = route?.path || ''
  return path === prefix || path.startsWith(prefix + '/')
}

const handleLogout = async () => {
  isMobileMenuOpen.value = false
  try {
    await logout(router)
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

// Any navigation closes both menus
watch(() => route?.fullPath, () => {
  isMobileMenuOpen.value = false
  isProductsMenuOpen.value = false
})

const handleScroll = () => {
  if (isProductsMenuOpen.value) {
    isProductsMenuOpen.value = false
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    isMobileMenuOpen.value = false
    isProductsMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<!-- Unscoped: the dropdown renders its own <button>, and .site-nav-link is
     that button's recipe too, so it is declared here once. -->
<style>
/* Doubled class so it outranks `.spotlight`'s own page background: these
   groups only borrow the tokens. */
.spotlight.site-nav-group {
  background: transparent;
}

.site-nav-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  color: var(--sl-muted);
  background: transparent;
  transition: color 0.2s cubic-bezier(0.22, 1, 0.36, 1), background-color 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.site-nav-link:hover,
.site-nav-link[aria-expanded='true'] {
  color: var(--sl-text);
  background: var(--sl-chip-bg-hover);
}

.site-nav-link.is-active {
  color: var(--sl-text);
  font-weight: 600;
}

/* Sign in: the ink pill. The bar leaves the coral light to the page. */
.site-nav-cta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2.25rem;
  padding: 0 1.125rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
  color: var(--sl-bg);
  background: var(--sl-text);
  transition: opacity 0.2s cubic-bezier(0.22, 1, 0.36, 1), transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.site-nav-cta:hover {
  opacity: 0.88;
  transform: translateY(-1px);
}

.site-nav-menu-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  height: 2.125rem;
  padding: 0 0.8rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong);
  background: var(--sl-chip-bg);
  color: var(--sl-text);
  font-size: 0.8125rem;
  font-weight: 600;
}

.site-nav-menu-btn i {
  font-size: 0.8rem;
  width: 0.9rem;
}

/* Phone sheet */
.site-sheet-scrim {
  position: fixed;
  inset: 3.5rem 0 0;
  z-index: 40;
  background: rgba(8, 9, 13, 0.35);
  backdrop-filter: blur(3px);
}

.spotlight.site-sheet {
  position: fixed;
  top: calc(3.5rem + 1px);
  left: 0;
  right: 0;
  z-index: 45;
  max-height: calc(100dvh - 3.5rem - 1px);
  overflow-y: auto;
  display: grid;
  gap: 0;
  padding: 0.5rem max(1.25rem, env(safe-area-inset-right, 0px)) 1.4rem max(1.25rem, env(safe-area-inset-left, 0px));
  background: var(--sl-surface);
  border-bottom: 1px solid var(--sl-line-strong);
  box-shadow: 0 24px 50px -22px rgba(0, 0, 0, 0.45);
}

.site-sheet__group {
  display: grid;
  gap: 2px;
  padding: 0.75rem 0 0.85rem;
  border-bottom: 1px solid var(--sl-line);
}

.site-sheet__label {
  margin: 0 0 0.25rem;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--sl-muted);
}

.site-sheet__link {
  padding: 0.45rem 0;
  font-size: 1.0625rem;
  font-weight: 600;
  color: var(--sl-muted);
}

.site-sheet__link.is-active,
.site-sheet__link:hover {
  color: var(--sl-text);
}

.site-sheet__actions {
  display: grid;
  gap: 0.625rem;
  margin-top: 1rem;
}

.site-sheet__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2.75rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong);
  background: var(--sl-chip-bg);
  color: var(--sl-text);
  font-size: 0.9375rem;
  font-weight: 600;
}

.site-sheet-enter-active,
.site-sheet-leave-active {
  transition: opacity 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.site-sheet-enter-from,
.site-sheet-leave-to {
  opacity: 0;
}

/* Product menu rows. They render inside the dropdown's .spotlight panel, so
   every colour is a --sl-* token and both themes come from spotlight.css. */
.nav-menu-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 10px 14px;
  border: 1px solid transparent;
  border-radius: 13px;
  text-align: left;
  transition: background-color 0.2s ease, border-color 0.2s ease;
}

.nav-menu-item:hover,
.nav-menu-item:focus-visible {
  background: var(--sl-chip-bg-hover);
  border-color: var(--sl-line);
}

.nav-menu-item__title {
  display: block;
  font-family: var(--sl-font-display);
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--sl-text);
}

.nav-menu-item__desc {
  display: block;
  margin-top: 1px;
  font-size: 13px;
  color: var(--sl-muted);
}

.nav-menu-item__arrow {
  margin-left: 8px;
  font-size: 11px;
  color: var(--sl-faint);
  transition: transform 0.2s ease, color 0.2s ease;
}

.nav-menu-item:hover .nav-menu-item__arrow,
.nav-menu-item:focus-visible .nav-menu-item__arrow {
  transform: translateX(3px);
  color: var(--sl-coral);
}

@media (prefers-reduced-motion: reduce) {
  .site-nav-cta:hover {
    transform: none;
  }
}
</style>
