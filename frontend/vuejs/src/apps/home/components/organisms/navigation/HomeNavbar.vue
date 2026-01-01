<!-- Home navigation component -->
<template>
  <BaseNavbar>
    <!-- Logo override -->
    <template #logo>
      <GradientText variant="imagi" size="xl">Imagi</GradientText>
    </template>

    <!-- Right side menu -->
    <template #right>
      <div class="flex items-center space-x-4">
        <!-- Products Dropdown - Only shown when authenticated -->
        <HomeNavbarDropdownButton
          v-if="isAuthenticated"
          v-model="isProductsMenuOpen"
          gradient-type="primary"
        >
          Products
          
          <template #menu>
            <router-link
              :to="{ name: 'builder-dashboard' }"
              class="group flex items-center gap-3 px-5 py-3.5 text-sm font-medium text-white/90 hover:text-white transition-all duration-300 hover:bg-gradient-to-r hover:from-primary-500/20 hover:via-indigo-500/20 hover:to-violet-500/20 relative overflow-hidden"
              @click="isProductsMenuOpen = false"
            >
              <!-- Hover glow effect -->
              <div class="absolute inset-0 bg-gradient-to-r from-primary-500/0 via-primary-500/5 to-primary-500/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              
              <!-- Icon with gradient on hover -->
              <div class="relative z-10 flex items-center justify-center w-8 h-8 rounded-lg bg-primary-500/10 group-hover:bg-primary-500/20 transition-all duration-300">
                <i class="fas fa-magic text-primary-400 group-hover:text-primary-300 transition-colors duration-300"></i>
              </div>
              
              <!-- Text -->
              <span class="relative z-10 flex-1">Oasis Web App Builder</span>
              
              <!-- Arrow indicator -->
              <i class="fas fa-arrow-right text-xs text-white/40 group-hover:text-white/80 transform group-hover:translate-x-1 transition-all duration-300 relative z-10"></i>
            </router-link>
          </template>
        </HomeNavbarDropdownButton>

        <!-- Buy Credits Button - Only shown when authenticated -->
        <HomeNavbarButton
          v-if="isAuthenticated"
          to="/payments/checkout"
          variant="primary"
          size="base"
          icon="fas fa-coins"
          gradient-type="amber"
        >
          Buy AI Credits
        </HomeNavbarButton>

        <!-- Auth Buttons -->
        <div class="flex items-center space-x-3">
          <template v-if="isAuthenticated">
            <HomeNavbarButton
              @click="handleLogout"
              variant="primary"
              size="base"
              icon="fas fa-sign-out-alt"
              gradient-type="indigo"
            >
              Logout
            </HomeNavbarButton>
          </template>
          <template v-else>
            <HomeNavbarButton
              to="/auth/login"
              variant="primary"
              size="base"
              icon="fas fa-sign-in-alt"
              gradient-type="indigo"
            >
              Sign In
            </HomeNavbarButton>
          </template>
        </div>
      </div>

      <!-- Overlay for closing dropdown when clicking outside -->
      <div
        v-if="isProductsMenuOpen"
        class="fixed inset-0 z-40"
        @click="isProductsMenuOpen = false"
      ></div>
    </template>
  </BaseNavbar>
</template>

<script>
import { defineComponent, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import { useAuth } from '@/apps/auth'
import BaseNavbar from '@/shared/components/organisms/navigation/BaseNavbar.vue'
import GradientText from '@/apps/home/components/atoms/text/GradientText.vue'
import IconButton from '@/apps/home/components/atoms/buttons/IconButton.vue'
import HomeNavbarButton from '@/apps/home/components/atoms/buttons/HomeNavbarButton.vue'
import HomeNavbarDropdownButton from '@/apps/home/components/atoms/buttons/HomeNavbarDropdownButton.vue'

export default defineComponent({
  name: 'HomeNavbar',
  components: {
    BaseNavbar,
    IconButton,
    HomeNavbarButton,
    HomeNavbarDropdownButton,
    GradientText
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
      router.push('/auth/login')
    }

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
