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
            <router-view v-slot="{ Component }">
              <transition
                name="page"
                mode="out-in"
              >
                <component :is="Component" />
              </transition>
            </router-view>
          </div>

          <!-- Links -->
          <AuthLinks 
            v-if="layoutConfig.mainLink"
            :main-link="layoutConfig.mainLink"
            :additional-links="layoutConfig.additionalLinks"
          />
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

<style>
.page-enter-active,
.page-leave-active {
  @apply transition-all duration-200 ease-out;
}

.page-enter-from {
  @apply opacity-0 translate-y-2;
}

.page-leave-to {
  @apply opacity-0 -translate-y-2;
}
</style> 