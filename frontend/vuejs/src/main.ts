import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from '@/router/index'
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { validationPlugin } from '@/apps/auth/plugins/validation'
import config from '@/shared/config'

// Import Tailwind styles
import 'tailwindcss/tailwind.css'

// Material and motion the whole site shares: the crisp-card shadow ladder, the
// film grain, the page-load rise, and the surface variable focus rings offset
// against. Unscoped on purpose — a card in the Sell workspace and a card on the
// pricing page are meant to cast the same shadow.
import '@/shared/styles/tokens.css'

// Design system for the public pages (home, about, pricing, docs, legal,
// auth). Scoped to `.editorial`, so the signed-in app is unaffected.
import '@/shared/styles/editorial.css'

// Note: icons are rendered as <i class="fas fa-…"> against the Font Awesome
// stylesheet loaded in index.html. The Vue component packages were registered
// here for a <font-awesome-icon> that no template ever used, so they and their
// ten-icon library are gone.

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

// Mount app
app.mount('#app')
