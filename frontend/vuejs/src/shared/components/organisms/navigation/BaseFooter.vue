<template>
  <footer class="bg-gradient-to-b from-dark-900 to-dark-950 border-t border-dark-700/30">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="py-8 grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
        <div class="col-span-1 space-y-4">
          <div class="space-y-3">
            <ImagiLogo size="md" />
            <p class="text-gray-400/90 leading-relaxed base font-light">
              Transform your ideas into powerful web applications using natural language with Imagi's AI technology.
            </p>
          </div>
        </div>

        <div class="col-span-1">
          <div class="space-y-4">
            <h4 class="text-xs font-semibold text-primary-400/90 uppercase tracking-wider">Learn</h4>
            <ul class="space-y-2.5">
              <li>
                <NavLink to="/docs">Documentation</NavLink>
              </li>
              <li>
                <NavLink to="/about">About Us</NavLink>
              </li>
              <li>
                <NavLink to="/contact">Contact</NavLink>
              </li>
            </ul>
          </div>
        </div>

        <div class="col-span-1">
          <div class="space-y-4">
            <h4 class="text-xs font-semibold text-primary-400/90 uppercase tracking-wider">Legal</h4>
            <ul class="space-y-2.5">
              <li>
                <NavLink to="/privacy">Privacy Policy</NavLink>
              </li>
              <li>
                <NavLink to="/terms">Terms of Service</NavLink>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div class="py-4 border-t border-dark-700/30">
        <p class="text-gray-400/80 text-xs text-center font-light">
          &copy; {{ currentYear }} Imagi. All rights reserved.
        </p>
      </div>
    </div>
  </footer>
</template>

<script>
import { defineComponent } from 'vue'
import { NavLink, ImagiLogo } from '@/shared/components/molecules'

export default defineComponent({
  name: 'BaseFooter',
  components: {
    NavLink,
    ImagiLogo
  },
  computed: {
    currentYear() {
      return new Date().getFullYear()
    }
  }
})
</script>
