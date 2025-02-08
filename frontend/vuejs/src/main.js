import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import validation plugin (update path)
import '@/apps/auth/plugins/validation'

// Import Tailwind styles
import 'tailwindcss/tailwind.css'

// Import Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faKeyboard, faBolt, faCode, faPencilAlt, 
  faMagic, faSlidersH, faRocket, faStore, 
  faBriefcase, faUsers, faChartLine, faArrowRight,
  faSignOutAlt, faUser, faCog, faCheck, faEnvelope,
  faPhone, faClock, faExclamationCircle, faBullseye,
  faStar, faRobot, faCodeBranch
} from '@fortawesome/free-solid-svg-icons'
import {
  faTwitter,
  faGithub,
  faLinkedin
} from '@fortawesome/free-brands-svg-icons'

// Add icons to library
library.add(
  faKeyboard, faBolt, faCode, faPencilAlt,
  faMagic, faSlidersH, faRocket, faStore,
  faBriefcase, faUsers, faChartLine, faArrowRight,
  faSignOutAlt, faUser, faCog, faCheck, faEnvelope,
  faPhone, faClock, faExclamationCircle, faBullseye,
  faStar, faRobot, faCodeBranch,
  faTwitter, faGithub, faLinkedin
)

// Configure axios
import axios from 'axios'
import config from '@/shared/config'

// Set base URL for API requests
axios.defaults.baseURL = config.apiUrl

// Configure Axios defaults
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'

// Create Vue app instance
const app = createApp(App)

// Add global properties
app.config.globalProperties.$axios = axios

// Global error handler
app.config.errorHandler = (error, vm, info) => {
  // Filter out extension-related errors
  if (error?.message?.toLowerCase().includes('extension') || 
      error?.message?.toLowerCase().includes('back/forward cache')) {
    return
  }
  
  // Log other errors
  console.error('Vue Error:', {
    error: error?.message || error,
    component: vm?.$options?.name || 'Unknown',
    info,
    url: window.location.href,
    timestamp: new Date().toISOString()
  })
}

// Use plugins
app.use(createPinia())
app.use(router)

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
function disableBFCache() {
  // Add meta tags to prevent caching
  const metaTags = [
    { httpEquiv: 'Cache-Control', content: 'no-store, no-cache, must-revalidate, proxy-revalidate' },
    { httpEquiv: 'Pragma', content: 'no-cache' },
    { httpEquiv: 'Expires', content: '0' }
  ];

  metaTags.forEach(({ httpEquiv, content }) => {
    let meta = document.querySelector(`meta[http-equiv="${httpEquiv}"]`);
    if (!meta) {
      meta = document.createElement('meta');
      meta.httpEquiv = httpEquiv;
      meta.content = content;
      document.head.appendChild(meta);
    }
  });

  // Disable service worker navigation preload
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(registration => {
      if ('navigationPreload' in registration) {
        registration.navigationPreload.disable();
      }
    });
  }

  // Force reload on back/forward navigation
  window.addEventListener('pageshow', (event) => {
    if (event.persisted || (window.performance && window.performance.navigation.type === 2)) {
      window.location.reload(true);
    }
  });

  // Force reload on popstate
  window.addEventListener('popstate', () => {
    window.location.reload(true);
  });
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
