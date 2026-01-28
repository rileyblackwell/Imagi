<!-- Home navigation component -->
<template>
  <BaseNavbar>
    <!-- Logo override -->
    <template #logo>
      <span class="text-xl font-bold text-black dark:text-white tracking-tight transition-colors duration-300">Imagi</span>
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
          Products
          
          <template #menu>
            <router-link
              :to="{ name: 'builder-dashboard' }"
              class="flex items-center justify-center px-3 py-2.5 text-sm font-semibold text-black rounded-lg mx-1 my-0.5 group"
              @click="isProductsMenuOpen = false"
            >
              <span class="tracking-wide">Imagi</span>
              <i class="fas fa-arrow-right text-xs ml-2 transition-transform duration-200 group-hover:translate-x-1"></i>
            </router-link>
          </template>
        </HomeNavbarDropdownButton>

        <!-- Purchase Credits Button - Only shown when authenticated -->
        <HomeNavbarButton
          v-if="isAuthenticated"
          to="/payments/checkout"
          variant="primary"
          size="base"
          gradient-type="minimal"
          text-style
        >
          Purchase AI Credits
        </HomeNavbarButton>
      </div>

      <!-- Overlay for closing dropdown when clicking outside -->
      <div
        v-if="isProductsMenuOpen"
        class="fixed inset-0 z-40"
        @click="isProductsMenuOpen = false"
      ></div>
    </template>

    <!-- Right side menu -->
    <template #right>
      <!-- Auth Buttons -->
      <div class="flex items-center space-x-3">
        <template v-if="isAuthenticated">
          <HomeNavbarButton
            @click="handleLogout"
            variant="primary"
            size="base"
            gradient-type="minimal"
          >
            Sign Out
          </HomeNavbarButton>
        </template>
        <template v-else>
          <HomeNavbarButton
            to="/auth/login"
            variant="primary"
            size="base"
            gradient-type="minimal"
          >
            Sign In
          </HomeNavbarButton>
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
      router.push('/auth/login')
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
