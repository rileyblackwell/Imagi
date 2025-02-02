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
            class="inline-flex items-center px-5 py-2.5 text-sm font-medium text-white rounded-lg transition-all duration-300 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 hover:shadow-lg hover:shadow-indigo-600/20"
            :class="{ 'shadow-lg shadow-indigo-600/20': isProductsMenuOpen }"
          >
            Products
            <i class="fas fa-chevron-down ml-2 text-xs" :class="{ 'transform rotate-180': isProductsMenuOpen }"></i>
          </button>

          <!-- Dropdown Menu -->
          <div
            v-show="isProductsMenuOpen"
            class="absolute right-0 mt-3 w-56 rounded-lg bg-gradient-to-b from-dark-800 to-dark-900 border border-dark-700/50 shadow-xl backdrop-blur-sm z-50"
          >
            <router-link
              :to="{ name: 'builder-landing' }"
              class="block px-5 py-3.5 text-sm text-gray-300 hover:text-white transition-all duration-300 rounded-lg hover:bg-gradient-to-r hover:from-indigo-600/20 hover:to-indigo-500/20"
              @click="isProductsMenuOpen = false"
            >
              <i class="fas fa-magic mr-2 text-indigo-400"></i>
              Oasis Web App Builder
            </router-link>
          </div>
        </div>

        <!-- Buy Credits Button - Only shown when authenticated -->
        <IconButton
          v-if="isAuthenticated"
          to="/payments/checkout"
          variant="primary"
          size="base"
          icon="fas fa-coins"
          class="bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-400 hover:to-yellow-400 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-amber-500/20 px-5 py-2.5"
        >
          Buy Credits
        </IconButton>

        <!-- Auth Buttons -->
        <div class="flex items-center space-x-3">
          <template v-if="isAuthenticated">
            <IconButton
              @click="handleLogout"
              variant="ghost"
              size="base"
              icon="fas fa-sign-out-alt"
              class="bg-gradient-to-r from-dark-800/50 to-dark-700/50 hover:from-dark-700/50 hover:to-dark-600/50 rounded-lg px-5 py-2.5 backdrop-blur-sm transition-all duration-300 border border-dark-700/30 hover:border-dark-600/50 shadow-lg hover:shadow-dark-600/10"
            >
              Logout
            </IconButton>
          </template>
          <template v-else>
            <IconButton
              to="/auth/login"
              variant="primary"
              size="base"
              icon="fas fa-sign-in-alt"
              class="bg-gradient-to-r from-primary-600 via-indigo-500 to-primary-500 hover:from-primary-500 hover:via-indigo-400 hover:to-primary-400 transform hover:scale-105 transition-all duration-300 shadow-lg hover:shadow-primary-600/20 px-5 py-2.5"
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
