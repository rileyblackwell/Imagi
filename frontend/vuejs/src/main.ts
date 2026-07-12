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
import { initViewportDebug } from '@/shared/debug/viewportDebug'

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

// Deploy identification: check the running bundle's build time from any device
// via the console or `document.documentElement.dataset.build`.
console.info(`Imagi build: ${__BUILD_TIME__}`)
document.documentElement.dataset.build = __BUILD_TIME__

// On-device diagnostics for the iPad render glitch — enable with ?debug=1.
initViewportDebug()

// NOTE: no scroll "nudges" on pageshow/tab-restore — deliberately. A
// programmatic scroll issued while iPad Chrome is mid tab-restore or mid
// toolbar animation is a prime suspect for wedging the browser's native
// scroll inset (scroll floor stuck at the toolbar height, ~132px, page top
// unreachable until the tab is re-activated). Page JS cannot undo that
// state once wedged, so nothing here may scroll during restore transitions.
