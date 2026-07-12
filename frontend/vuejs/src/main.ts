import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from '@/router/index'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { validationPlugin } from '@/apps/auth/plugins/validation'
import config from '@/shared/config'

// Import Tailwind styles
import 'tailwindcss/tailwind.css'
// Global document styles (single window scroller, scrollbars, focus, dvh fixes).
// Must come after Tailwind so its .min-h-screen dvh override wins the cascade.
import '@/assets/main.css'

// Import Font Awesome icons
import {
  faUser,
  faLock,
  faCircleNotch,
  faExclamationCircle,
  faCheckCircle,
  faSpinner,
  faEye,
  faEyeSlash,
  faSun,
  faMoon
} from '@fortawesome/free-solid-svg-icons'

// Add icons to library
library.add(
  faUser,
  faLock,
  faCircleNotch,
  faExclamationCircle,
  faCheckCircle,
  faSpinner,
  faEye,
  faEyeSlash,
  faSun,
  faMoon
)

// Configure axios
axios.defaults.baseURL = config.apiUrl
axios.defaults.withCredentials = true
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

// Type augmentation for Vue
declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $axios: AxiosInstance;
  }
}

// Create Vue app instance
const app = createApp(App)
const pinia = createPinia()

// Add global properties
app.config.globalProperties.$axios = axios

// Use plugins
app.use(pinia)
app.use(router)
app.use(validationPlugin)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Mount app
app.mount('#app')

// iOS/iPadOS WebKit can restore a page (back-swipe bfcache) with stale
// compositing/viewport state — content renders clipped or offset until the
// engine re-composites (the same glitch a tab switch clears). Nudging the
// scroll position on restore forces that re-composite immediately.
window.addEventListener('pageshow', (event) => {
  if (event.persisted) {
    requestAnimationFrame(() => {
      window.scrollTo(window.scrollX, window.scrollY + 1)
      window.scrollTo(window.scrollX, Math.max(0, window.scrollY - 1))
    })
  }
})
