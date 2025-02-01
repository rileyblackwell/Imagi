<!-- Auth Layout -->
<template>
  <DefaultLayout>
    <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-dark-950 to-dark-900">
      <div class="w-full max-w-md">
        <div class="auth-form-container">
          <!-- Header -->
          <AuthHeader 
            :title="layoutConfig.title"
            :subtitle="layoutConfig.subtitle"
          />

          <!-- Main Content -->
          <div class="mt-8">
            <router-view v-slot="{ Component }">
              <component :is="Component" />
            </router-view>
          </div>

          <!-- Links -->
          <AuthLinks
            :main-text="layoutConfig.mainText"
            :main-link="layoutConfig.mainLink"
          >
            <template #additional-links>
              <template v-if="layoutConfig.additionalLinks">
                <component
                  v-for="(link, index) in layoutConfig.additionalLinks"
                  :key="index"
                  :is="link.type || 'router-link'"
                  :to="link.to"
                  :class="link.class || 'text-gray-400 hover:text-gray-300'"
                >
                  {{ link.text }}
                </component>
              </template>
            </template>
          </AuthLinks>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DefaultLayout } from '@/shared/layouts'
import AuthHeader from '../components/AuthHeader.vue'
import AuthLinks from '../components/AuthLinks.vue'

export default {
  name: 'AuthLayout',
  components: {
    DefaultLayout,
    AuthHeader,
    AuthLinks
  },
  setup() {
    const route = useRoute()
    
    const layoutConfig = computed(() => {
      return route.matched[route.matched.length - 1].components.default.layoutConfig || {
        title: '',
        subtitle: '',
        mainText: '',
        mainLink: { to: '', text: '' },
        additionalLinks: []
      }
    })

    return {
      layoutConfig
    }
  }
}
</script>

<style scoped>
.auth-form-container {
  @apply w-full p-8 bg-dark-900 bg-opacity-50 backdrop-blur-sm border border-dark-700 rounded-2xl shadow-xl;
}

/* Page transition animations */
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style> 