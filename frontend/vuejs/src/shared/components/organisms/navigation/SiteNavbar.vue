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

    <!-- Product and Pricing are for the signed-in, centred in the bar.
         !bg-transparent outranks `.spotlight`'s own page background: these
         groups only borrow the tokens. -->
    <template #center>
      <div v-if="isAuthenticated" class="spotlight !bg-transparent hidden md:flex items-center gap-1">
        <SiteNavbarDropdown v-model="isProductsMenuOpen" :active="isActive('/imagi')">
          Product

          <template #menu>
            <!-- Product menu rows. They render inside the dropdown's .spotlight
                 panel, so every colour is a --sl-* token. -->
            <router-link
              :to="{ name: 'builder' }"
              class="group flex items-center gap-[14px] py-[10px] px-[14px] border border-transparent rounded-[13px] text-left
                     [transition:background-color_0.2s_ease,border-color_0.2s_ease]
                     hover:bg-sl-chip-bg-hover hover:border-sl-line focus-visible:bg-sl-chip-bg-hover focus-visible:border-sl-line"
              @click="isProductsMenuOpen = false"
            >
              <span class="min-w-0 flex-1">
                <span class="block font-sl-display text-[15px] font-semibold tracking-[-0.01em] text-sl-text">Imagi</span>
                <span class="block mt-px text-[13px] text-sl-muted">Build and <em class="sl-run">run</em> your business</span>
              </span>
              <i
                class="fas fa-arrow-right ml-2 text-[11px] text-sl-faint [transition:transform_0.2s_ease,color_0.2s_ease]
                       group-hover:translate-x-[3px] group-hover:text-sl-coral group-focus-visible:translate-x-[3px] group-focus-visible:text-sl-coral"
                aria-hidden="true"
              ></i>
            </router-link>
          </template>
        </SiteNavbarDropdown>

        <router-link
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          :class="[navLink, isActive(link.match) ? 'is-active text-sl-text font-semibold' : 'text-sl-muted font-medium']"
          :aria-current="isActive(link.match) ? 'page' : undefined"
        >
          {{ link.label }}
        </router-link>
      </div>
    </template>

    <template #right>
      <div class="spotlight !bg-transparent flex items-center gap-3">
        <template v-if="isAuthenticated">
          <div class="hidden md:flex">
            <button type="button" :class="[navLink, 'text-sl-muted font-medium']" @click="handleLogout">Sign out</button>
          </div>

          <button
            type="button"
            class="inline-flex md:hidden items-center gap-[0.45rem] h-[2.125rem] px-[0.8rem] rounded-full border border-sl-line-strong bg-sl-chip-bg text-sl-text text-[0.8125rem] font-semibold"
            :aria-expanded="isMobileMenuOpen ? 'true' : 'false'"
            aria-controls="site-nav-sheet"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
          >
            <i class="fas text-[0.8rem] w-[0.9rem]" :class="isMobileMenuOpen ? 'fa-xmark' : 'fa-bars'" aria-hidden="true"></i>
            {{ isMobileMenuOpen ? 'Close' : 'Menu' }}
          </button>
        </template>
        <!-- Visitors have one thing to do here, so it is the bar's one button:
             the ink pill. The bar leaves the coral light to the page. -->
        <router-link v-else to="/auth/signin" :class="[navCta, 'h-9 text-[0.875rem]']">Sign in</router-link>
      </div>
    </template>
  </BaseNavbar>

  <!-- Phone menu, signed in only: a sheet hung under the bar over a soft scrim -->
  <transition
    enter-active-class="[transition:opacity_0.2s_cubic-bezier(0.22,1,0.36,1)]"
    leave-active-class="[transition:opacity_0.2s_cubic-bezier(0.22,1,0.36,1)]"
    enter-from-class="opacity-0"
    leave-to-class="opacity-0"
  >
    <div v-if="isAuthenticated && isMobileMenuOpen" class="md:hidden">
      <div class="fixed inset-x-0 top-14 bottom-0 z-40 bg-[rgba(8,9,13,0.35)] backdrop-blur-[3px]" @click="isMobileMenuOpen = false"></div>
      <div
        id="site-nav-sheet"
        class="spotlight fixed top-nav left-0 right-0 z-[45] max-h-[calc(100dvh-3.5rem-1px)] overflow-y-auto grid gap-0
               pt-2 pb-[1.4rem] pr-[max(1.25rem,env(safe-area-inset-right,0px))] pl-[max(1.25rem,env(safe-area-inset-left,0px))]
               !bg-sl-surface border-b border-b-sl-line-strong [box-shadow:0_24px_50px_-22px_rgba(0,0,0,0.45)]"
      >
        <div class="grid gap-[2px] pt-3 pb-[0.85rem] border-b border-b-sl-line">
          <p class="mb-1 text-[11px] font-semibold tracking-[0.16em] uppercase text-sl-muted">Product</p>
          <router-link
            :to="{ name: 'builder' }"
            :class="[sheetLink, isActive('/imagi') ? 'is-active text-sl-text' : 'text-sl-muted hover:text-sl-text']"
          >
            Imagi
          </router-link>
          <router-link
            to="/payments/pricing"
            :class="[sheetLink, isActive('/payments') ? 'is-active text-sl-text' : 'text-sl-muted hover:text-sl-text']"
          >
            Pricing
          </router-link>
        </div>

        <div class="grid gap-[0.625rem] mt-4">
          <button type="button" :class="sheetBtn" @click="handleLogout">Sign out</button>
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

// The bar's quiet link. SiteNavbarDropdown's trigger wears the same recipe.
// `site-nav-link` / `site-nav-cta` are kept as hooks (the specs find by them).
const navLink =
  'site-nav-link inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-full text-[0.875rem] whitespace-nowrap bg-transparent ' +
  '[transition:color_0.2s_cubic-bezier(0.22,1,0.36,1),background-color_0.2s_cubic-bezier(0.22,1,0.36,1)] ' +
  'hover:text-sl-text hover:bg-sl-chip-bg-hover'

// The ink pill; each caller adds its height and text size
const navCta =
  'site-nav-cta inline-flex items-center justify-center px-[1.125rem] rounded-full font-semibold whitespace-nowrap text-sl-bg bg-sl-text ' +
  '[transition:opacity_0.2s_cubic-bezier(0.22,1,0.36,1),transform_0.2s_cubic-bezier(0.22,1,0.36,1)] ' +
  'hover:opacity-[0.88] hover:-translate-y-px motion-reduce:hover:transform-none'

const sheetLink = 'py-[0.45rem] text-[1.0625rem] font-semibold'

const sheetBtn =
  'inline-flex items-center justify-center h-11 rounded-full border border-sl-line-strong bg-sl-chip-bg text-sl-text text-[0.9375rem] font-semibold'

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
