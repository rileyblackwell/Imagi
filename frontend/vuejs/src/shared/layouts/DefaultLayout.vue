<template>
  <BaseLayout>
    <!-- Header -->
    <HomeNavbar v-if="isHomeNav" />
    <BaseNavbar v-else />

    <!-- Main Content with Transition -->
    <main class="flex-1 relative">
      <transition
        name="page"
        mode="out-in"
        @before-enter="beforeEnter"
        @enter="enter"
        @after-enter="afterEnter"
        @enter-cancelled="enterCancelled"
        @before-leave="beforeLeave"
        @leave="leave"
        @after-leave="afterLeave"
        @leave-cancelled="leaveCancelled"
      >
        <slot></slot>
      </transition>
    </main>

    <!-- Footer -->
    <BaseFooter class="z-10 relative" />
  </BaseLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { BaseLayout } from '@/shared/layouts'
import { BaseNavbar, BaseFooter } from '@/shared/components'
import HomeNavbar from '@/apps/home/components/organisms/navigation/HomeNavbar.vue'
import gsap from 'gsap'

export default {
  name: 'DefaultLayout',
  components: {
    BaseLayout,
    BaseNavbar,
    BaseFooter,
    HomeNavbar
  },
  props: {
    isHomeNav: {
      type: Boolean,
      default: false
    }
  },
  setup() {
    const isEntered = ref(false)

    onMounted(() => {
      // Set isEntered to true after mount to trigger initial animation
      setTimeout(() => {
        isEntered.value = true
      }, 100)
    })

    return { isEntered }
  },
  methods: {
    beforeEnter(el) {
      gsap.set(el, {
        opacity: 0,
        y: 10
      })
    },
    enter(el, done) {
      gsap.to(el, {
        duration: 0.3,
        opacity: 1,
        y: 0,
        onComplete: done,
        ease: 'power2.out'
      })
    },
    afterEnter(el) {
      // Cleanup if needed
    },
    enterCancelled(el) {
      // Handle cancellation if needed
    },
    beforeLeave(el) {
      el.style.opacity = 1
    },
    leave(el, done) {
      gsap.to(el, {
        duration: 0.2,
        opacity: 0,
        y: -10,
        onComplete: done,
        ease: 'power2.in'
      })
    },
    afterLeave(el) {
      // Cleanup if needed
    },
    leaveCancelled(el) {
      // Handle cancellation if needed
    }
  }
}
</script>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>