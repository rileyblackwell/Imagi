<!-- Home navigation component -->
<template>
  <BaseNavbar>
    <!-- Logo override -->
    <template #logo>
      <GradientText variant="primary" size="xl">Imagi</GradientText>
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
              :to="{ name: 'builder-landing' }"
              class="block px-5 py-3 text-sm text-white/80 hover:text-white transition-all duration-200 hover:bg-gradient-to-r hover:from-primary-500/10 hover:via-indigo-500/10 hover:to-violet-500/10"
              @click="isProductsMenuOpen = false"
            >
              <i class="fas fa-magic mr-2 text-primary-400"></i>
              Oasis Web App Builder
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
          Buy Credits
        </HomeNavbarButton>

        <!-- Auth Buttons -->
        <div class="flex items-center space-x-3">
          <template v-if="isAuthenticated">
            <HomeNavbarButton
              @click="handleLogout"
              variant="ghost"
              size="base"
              icon="fas fa-sign-out-alt"
              gradient-type="primary"
            >
              Logout
            </HomeNavbarButton>
          </template>
          <template v-else>
            <HomeNavbarButton
              to="/auth/login"
              variant="ghost"
              size="base"
              icon="fas fa-sign-in-alt"
              gradient-type="primary"
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
import { computed, ref, defineComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'
import { BaseNavbar } from '@/shared/components'
import IconButton from '@/apps/home/components/shared/IconButton.vue'
import HomeNavbarButton from '@/apps/home/components/shared/HomeNavbarButton.vue'
import GradientText from '@/apps/home/components/shared/GradientText.vue'
import HomeNavbarDropdownButton from '@/apps/home/components/shared/HomeNavbarDropdownButton.vue'

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
    const isProductsMenuOpen = ref(false)

    const handleLogout = async () => {
      try {
        await authStore.logout()
        router.push('/auth/login')
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
