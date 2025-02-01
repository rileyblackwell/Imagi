<!-- Default layout for public pages -->
<template>
  <BaseLayout>
    <!-- Header -->
    <BaseNavbar :isHomeNav="isHomeNav" />

    <!-- Main Content with Transition -->
    <main class="flex-grow">
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
    <BaseFooter />
  </BaseLayout>
</template>

<script>
import { BaseLayout } from './index'
import { BaseNavbar, BaseFooter } from '@/shared/components'
import gsap from 'gsap'

export default {
  name: 'DefaultLayout',
  components: {
    BaseLayout,
    BaseNavbar,
    BaseFooter
  },
  props: {
    isHomeNav: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  },
  methods: {
    beforeEnter(el) {
      el.style.opacity = 0
      el.style.transform = 'translateY(10px)'
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

<style>
/* Transition classes */
.page-enter-active,
.page-leave-active {
  transition: opacity var(--transition-smooth), transform var(--transition-smooth);
}

.page-enter-from,
.page-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style> 