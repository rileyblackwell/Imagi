<template>
  <div id="app" class="min-h-screen bg-light-50 dark:bg-dark-950 text-gray-900 dark:text-white flex flex-col transition-colors duration-300">
    <router-view v-slot="{ Component }" class="flex-grow">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
    <NotificationToast />
  </div>
</template>

<script setup lang="ts">
import { NotificationToast } from '@/shared/components/atoms';
import { useAuthStore } from '@/shared/stores/auth';
import { useBalanceStore } from '@/shared/stores/balance';
import { useThemeStore } from '@/shared/stores/theme';
import { onMounted, onBeforeUnmount, watch, ref } from 'vue';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const balanceStore = useBalanceStore();
const themeStore = useThemeStore();
const router = useRouter();
const isNavigating = ref(false);

// Handle back/forward navigation events
const handlePopState = async (event: PopStateEvent) => {
  // console.log('Navigation event detected (popstate)');
  isNavigating.value = true;
  
  try {
    // If we have a token in localStorage but auth state says we're not authenticated,
    // restore the auth state without making an API call
    const tokenData = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (tokenData && userData && !authStore.isAuthenticated) {
      // console.log('Restoring auth state from localStorage during navigation');
      const token = JSON.parse(tokenData)?.value;
      const user = JSON.parse(userData);
      
      if (token && user) {
        // Just restore the state without calling the backend
        authStore.restoreAuthState(user, token);
      }
    }
  } catch (error) {
    console.error('Error handling navigation:', error);
  } finally {
    isNavigating.value = false;
  }
};

// Watch for route changes
watch(() => router.currentRoute.value.fullPath, () => {
  // Check if we need to restore auth state
  const tokenData = localStorage.getItem('token');
  const userData = localStorage.getItem('user');
  
  if (tokenData && userData && !authStore.isAuthenticated) {
    try {
      const token = JSON.parse(tokenData)?.value;
      const user = JSON.parse(userData);
      
      if (token && user) {
        authStore.restoreAuthState(user, token);
      }
    } catch (error) {
      // Handle error silently
    }
  }
});

onMounted(async () => {
  try {
    // Initialize theme first (before other UI elements)
    themeStore.initializeTheme();
    
    // Initialize auth state on app mount
    await authStore.initAuth();
    
    // Remove automatic balance initialization - balance should only be fetched
    // when user visits specific pages (payments/checkout, builder workspace) or
    // after specific actions (adding money, using AI models)
    
    // Add event listeners for browser navigation
    window.addEventListener('popstate', handlePopState);
    
    // Also listen for beforeunload event
    window.addEventListener('beforeunload', () => {
      // Make sure auth state is saved before unload
      if (authStore.token && authStore.user) {
        localStorage.setItem('user', JSON.stringify(authStore.user));
      }
    });
  } catch (error) {
    // Handle error silently
  }
});

// Watch for changes in authentication state to reset balance when logged out
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (!isAuthenticated) {
    // Only reset balance when user logs out - don't fetch when logging in
    balanceStore.resetBalance();
  }
});

onBeforeUnmount(() => {
  // Clean up event listeners
  window.removeEventListener('popstate', handlePopState);
  window.removeEventListener('beforeunload', () => {});
});
</script>

