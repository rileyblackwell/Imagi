<!-- Home navigation component -->
<template>
  <BaseNavbar fluid>
    <!-- Center menu -->
    <template #center>
      <div class="flex items-center space-x-4">
        <!-- Products Dropdown - Only shown when authenticated -->
        <HomeNavbarDropdownButton
          v-if="isAuthenticated"
          v-model="isProductsMenuOpen"
          gradient-type="minimal"
          text-style
        >
          Product

          <template #menu>
            <router-link
              :to="{ name: 'builder' }"
              class="group flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors duration-200 hover:bg-blue-50 dark:hover:bg-blue-400/10"
              @click="isProductsMenuOpen = false"
            >
              <span class="min-w-0">
                <span class="block text-sm font-semibold tracking-tight text-blue-950 dark:text-white">Imagi</span>
                <span class="block text-xs text-blue-950/60 dark:text-blue-100/60">Build and run your business</span>
              </span>
              <i class="fas fa-arrow-right text-xs text-blue-950/40 dark:text-blue-100/40 transition-all duration-200 group-hover:translate-x-0.5 group-hover:text-blue-600 dark:group-hover:text-blue-300"></i>
            </router-link>
          </template>
        </HomeNavbarDropdownButton>

        <!-- Pricing Button - Only shown when authenticated -->
        <HomeNavbarButton
          v-if="isAuthenticated"
          to="/payments/pricing"
          variant="primary"
          size="base"
          gradient-type="minimal"
          text-style
        >
          Pricing
        </HomeNavbarButton>
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
            class="inline-flex items-center justify-center px-5 py-2 rounded-full font-medium text-sm border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          >
            Sign Out
          </button>
        </template>
        <template v-else>
          <!-- Sign In: small navy ink pill — the one conversion action in the bar -->
          <router-link
            to="/auth/signin"
            class="inline-flex items-center justify-center px-5 py-2 rounded-full font-medium text-sm bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
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
import BaseNavbar from '@/shared/components/organisms/navigation/BaseNavbar.vue'
import HomeNavbarButton from '@/apps/home/components/atoms/buttons/HomeNavbarButton.vue'
import HomeNavbarDropdownButton from '@/apps/home/components/atoms/buttons/HomeNavbarDropdownButton.vue'

export default defineComponent({
  name: 'HomeNavbar',
  components: {
    BaseNavbar,
    HomeNavbarButton,
    HomeNavbarDropdownButton
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

    const toggleProductsMenu = () => {
      isProductsMenuOpen.value = !isProductsMenuOpen.value
    }

    const navigateToLogin = () => {
      router.push('/auth/signin')
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
      toggleProductsMenu,
      handleLogout,
      navigateToLogin,
      router
    }
  }
})
</script>

<style scoped>
/* Add transition for dropdown chevron */
.fa-chevron-down {
  transition: transform 0.2s ease-in-out;
}
</style>
