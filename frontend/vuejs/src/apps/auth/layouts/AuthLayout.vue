<!-- Auth Layout -->
<template>
  <DefaultLayout>
    <div class="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-dark-950 to-dark-900">
      <div class="w-full max-w-md">
        <div class="w-full p-8 bg-dark-900/50 backdrop-blur-sm border border-dark-700 rounded-2xl shadow-xl">
          <!-- Header -->
          <AuthHeader 
            :title="layoutConfig.title"
            :subtitle="layoutConfig.subtitle"
          />

          <!-- Main Content -->
          <div class="mt-8">
            <router-view v-slot="{ Component, route }">
              <transition name="fade" mode="out-in">
                <component 
                  :is="Component" 
                  :key="route.path"
                />
              </transition>
            </router-view>
          </div>

          <!-- Links -->
          <AuthLinks 
            v-if="layoutConfig.mainLink"
            :main-text="layoutConfig.mainText"
            :main-link="layoutConfig.mainLink"
            :additional-links="layoutConfig.additionalLinks"
          >
            <template v-slot:additional-links>
              <router-link 
                v-for="link in layoutConfig.additionalLinks"
                :key="link.to"
                :to="link.to"
                class="text-gray-400 hover:text-gray-300"
              >
                {{ link.text }}
              </router-link>
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
      const currentRoute = route.matched[route.matched.length - 1]
      const component = currentRoute?.components?.default
      return {
        title: component?.layoutConfig?.title || '',
        subtitle: component?.layoutConfig?.subtitle || '',
        mainText: component?.layoutConfig?.mainText || '',
        mainLink: component?.layoutConfig?.mainLink || { to: '', text: '' },
        additionalLinks: component?.layoutConfig?.additionalLinks || []
      }
    })

    return {
      layoutConfig
    }
  }
}
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style> 