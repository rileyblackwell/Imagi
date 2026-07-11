<!-- Home navigation component -->
<template>
  <BaseNavbar fluid>
    <!-- Logo override -->
    <template #logo>
      <span class="text-xl font-bold text-blue-950 dark:text-white tracking-tight transition-colors duration-300">Imagi</span>
    </template>

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
          <button
            type="button"
            @click="handleLogout"
            class="btn-3d btn-accent group relative inline-flex items-center justify-center min-w-[100px] px-6 py-2.5 text-blue-950 rounded-full font-medium text-sm overflow-hidden border border-white/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          >
            <!-- Top edge highlight for 3D effect -->
            <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
            <!-- Bottom edge shadow for depth -->
            <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
            <span class="relative">Sign Out</span>
          </button>
        </template>
        <template v-else>
          <router-link
            to="/auth/signin"
            class="btn-3d btn-accent group relative inline-flex items-center justify-center min-w-[100px] px-6 py-2.5 text-blue-950 rounded-full font-medium text-sm overflow-hidden border border-white/60 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          >
            <!-- Top edge highlight for 3D effect -->
            <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
            <!-- Bottom edge shadow for depth -->
            <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
            <span class="relative">Sign In</span>
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
import IconButton from '@/apps/home/components/atoms/buttons/IconButton.vue'
import HomeNavbarButton from '@/apps/home/components/atoms/buttons/HomeNavbarButton.vue'
import HomeNavbarDropdownButton from '@/apps/home/components/atoms/buttons/HomeNavbarDropdownButton.vue'

export default defineComponent({
  name: 'HomeNavbar',
  components: {
    BaseNavbar,
    IconButton,
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

/* Soft 3D button effect matching the hero "Start Building" button - blue-tinted shadows for the baby-blue fill. */
.btn-3d {
  transform: translateY(0) translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-3d:active {
  transform: translateY(0) translateZ(0);
  transition-duration: 0.1s;
}

/* Soft baby-blue gradient fill */
.btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

.dark .btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

/* On dark, ground the light button with deep neutral shadows; keep the inner sheen */
.dark .btn-3d {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 10px 20px -6px rgba(0, 0, 0, 0.5),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
}
</style>
