<!-- The site's main top bar: brand, the Product menu, Pricing, and the session
     controls. Used by every page that is not sign-in or checkout — home, the
     project hub, and the three tool workspaces — via DefaultLayout.

     It lived under apps/home until its consumers outgrew that name: a shared
     layout was reaching into one app's folder to render chrome that four apps
     were using. -->
<template>
  <BaseNavbar fluid>
    <!-- Center menu -->
    <template #center>
      <div class="flex items-center space-x-4">
        <!-- Products Dropdown - Only shown when authenticated -->
        <SiteNavbarDropdown v-if="isAuthenticated" v-model="isProductsMenuOpen">
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

        <!-- Pricing link - Only shown when authenticated -->
        <router-link
          v-if="isAuthenticated"
          to="/payments/pricing"
          class="site-nav-link"
        >
          Pricing
        </router-link>
      </div>
    </template>

    <!-- Right side menu -->
    <template #right>
      <!-- Auth Buttons -->
      <div class="flex items-center space-x-3">
        <template v-if="isAuthenticated">
          <!-- Sign Out: quiet hairline pill — a non-promoted action -->
          <button
            type="button"
            @click="handleLogout"
            class="inline-flex items-center justify-center px-5 py-2 rounded-full font-medium text-sm border border-ink/[0.14] text-ink/80 hover:text-ink hover:border-ink/30 hover:bg-ink/[0.03] dark:border-white/[0.16] dark:text-bone/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] transition-colors duration-200 focus-ring"
          >
            Sign Out
          </button>
        </template>
        <template v-else>
          <!-- Sign In: small navy ink pill — the one conversion action in the bar -->
          <router-link
            to="/auth/signin"
            class="inline-flex items-center justify-center px-5 py-2 rounded-full font-medium text-sm bg-ink text-paper hover:bg-blue-900 dark:bg-paper-inverted dark:text-ink dark:hover:bg-white transition-colors duration-200 shadow-[0_1px_2px_rgba(19,26,44,0.2),0_3px_8px_-2px_rgba(19,26,44,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-ring"
          >
            Sign In
          </router-link>
        </template>
      </div>
    </template>
  </BaseNavbar>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import { useAuth } from '@/apps/auth'
import BaseNavbar from './BaseNavbar.vue'
import SiteNavbarDropdown from './SiteNavbarDropdown.vue'

export default defineComponent({
  name: 'SiteNavbar',
  components: {
    BaseNavbar,
    SiteNavbarDropdown
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const { logout } = useAuth()
    const isProductsMenuOpen = ref(false)

    const handleLogout = async () => {
      try {
        // Pass router to the logout function
        await logout(router)
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }

    // Close dropdown on scroll
    const handleScroll = () => {
      if (isProductsMenuOpen.value) {
        isProductsMenuOpen.value = false
      }
    }

    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
    })

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })

    return {
      isAuthenticated: computed(() => authStore.isAuthenticated),
      isProductsMenuOpen,
      handleLogout
    }
  }
})
</script>

<!-- Unscoped: the dropdown renders its own <button>, and this is that
     button's recipe too. HomeNavbar is the dropdown's only caller, so the
     class is declared here once rather than copied into both components.

     The two centre items used to come from two different components and
     disagreed by accident — 16px of horizontal padding on one, 12px on the
     other, 8px of gap against 6px — because each inherited a different half
     of a gradient-button abstraction that neither of them used. -->
<style>
.site-nav-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: rgb(19, 26, 44);
  background: transparent;
  transition: opacity 0.2s ease;
}

.dark .site-nav-link {
  color: #ffffff;
}

.site-nav-link:hover {
  opacity: 0.7;
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
</style>
