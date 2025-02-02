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
        <div v-if="isAuthenticated" class="relative">
          <button
            @click="toggleProductsMenu"
            class="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-300 hover:text-white transition-colors"
            :class="{ 'text-white': isProductsMenuOpen }"
          >
            Products
            <i class="fas fa-chevron-down ml-2 text-xs" :class="{ 'transform rotate-180': isProductsMenuOpen }"></i>
          </button>

          <!-- Dropdown Menu -->
          <div
            v-show="isProductsMenuOpen"
            class="absolute right-0 mt-2 w-56 rounded-lg bg-dark-800 border border-dark-700 shadow-lg z-50"
          >
            <router-link
              :to="{ name: 'builder-landing' }"
              class="block px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-dark-700 transition-colors rounded-lg"
              @click="isProductsMenuOpen = false"
            >
              <i class="fas fa-magic mr-2"></i>
              Oasis Web App Builder
            </router-link>
          </div>
        </div>

        <!-- Buy Credits Button - Only shown when authenticated -->
        <IconButton
          v-if="isAuthenticated"
          to="/payments/checkout"
          variant="outline"
          size="sm"
          icon="fas fa-coins"
        >
          Buy Credits
        </IconButton>

        <!-- Auth Buttons -->
        <div class="flex items-center space-x-2">
          <template v-if="isAuthenticated">
            <IconButton
              @click="handleLogout"
              variant="ghost"
              size="sm"
              icon="fas fa-sign-out-alt"
            >
              Logout
            </IconButton>
          </template>
          <template v-else>
            <IconButton
              to="/auth/login"
              variant="ghost"
              size="sm"
              icon="fas fa-sign-in-alt"
            >
              Sign In
            </IconButton>
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
import GradientText from '@/apps/home/components/shared/GradientText.vue'

export default defineComponent({
  name: 'HomeNavbar',
  components: {
    BaseNavbar,
    IconButton,
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
