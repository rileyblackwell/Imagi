import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from '@/router/index'  // Update import path
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { validationPlugin } from '@/apps/auth/plugins/validation'
import config from '@/shared/config'

// Import Tailwind styles
import 'tailwindcss/tailwind.css'

// Import Font Awesome icons
import { 
  faUser, 
  faLock, 
  faCircleNotch,
  faExclamationCircle,
  faCheckCircle,
  faSpinner,
  faEye,
  faEyeSlash 
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
  faEyeSlash
)

// Configure axios
axios.defaults.baseURL = config.apiUrl
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
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

// Global error handler
interface ErrorInfo {
  error: string;
  component: string;
  info: string;
  url: string;
  timestamp: string;
}

app.config.errorHandler = (error: unknown, vm: any, info: string): void => {
  // Filter out extension-related errors
  if (error instanceof Error && 
     (error.message.toLowerCase().includes('extension') || 
      error.message.toLowerCase().includes('back/forward cache'))) {
    return
  }
  
  // Log other errors
  const errorLog: ErrorInfo = {
    error: error instanceof Error ? error.message : String(error),
    component: vm?.$options?.name || 'Unknown',
    info,
    url: window.location.href,
    timestamp: new Date().toISOString()
  }
  
  console.error('Vue Error:', errorLog)
}

// Use plugins
app.use(pinia)
app.use(router)
app.use(validationPlugin)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Performance monitoring
if (process.env.NODE_ENV === 'production') {
  // Add performance marks
  performance.mark('app-start')
  
  router.beforeEach(() => {
    performance.mark('route-start')
  })
  
  router.afterEach(() => {
    performance.mark('route-end')
    performance.measure('route-change', 'route-start', 'route-end')
  })
  
  app.mixin({
    mounted() {
      performance.mark('component-mounted')
      performance.measure('component-render', 'route-start', 'component-mounted')
    }
  })
}

// Cache control
function disableBFCache(): void {
  interface MetaTag {
    httpEquiv: string;
    content: string;
  }

  const metaTags: MetaTag[] = [
    { httpEquiv: 'Cache-Control', content: 'no-store, no-cache, must-revalidate, proxy-revalidate' },
    { httpEquiv: 'Pragma', content: 'no-cache' },
    { httpEquiv: 'Expires', content: '0' }
  ]

  metaTags.forEach(({ httpEquiv, content }) => {
    let meta = document.querySelector(`meta[http-equiv="${httpEquiv}"]`) as HTMLMetaElement | null
    if (!meta) {
      meta = document.createElement('meta')
      meta.setAttribute('http-equiv', httpEquiv)
      meta.setAttribute('content', content)
      document.head.appendChild(meta)
    }
  })

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(registration => {
      if ('navigationPreload' in registration) {
        registration.navigationPreload.disable()
      }
    })
  }

  window.addEventListener('pageshow', (event) => {
    if (event.persisted || (window.performance && window.performance.navigation.type === 2)) {
      window.location.reload()
    }
  })

  window.addEventListener('popstate', () => {
    window.location.reload()
  })
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', disableBFCache)
} else {
  disableBFCache()
}

// Mount app
performance.mark('app-init')
app.mount('#app')
performance.mark('app-mounted')
performance.measure('app-total-init', 'app-init', 'app-mounted')
