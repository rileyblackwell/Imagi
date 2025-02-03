import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

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

// Global error handler
app.config.errorHandler = (error, vm, info) => {
  if (
    error?.message?.includes('runtime.lastError') ||
    error?.message?.includes('extension port') ||
    error?.message?.includes('message port closed') ||
    error?.message?.includes('receiving end does not exist') ||
    error?.message?.includes('back/forward cache')
  ) {
    // Ignore extension-related errors
    return
  }
  console.error('Vue Error:', error)
  console.error('Component:', vm)
  console.error('Error Info:', info)
}

// Use plugins
app.use(createPinia())
app.use(router)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Disable bfcache for all pages
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', disableBFCache);
} else {
  disableBFCache();
}

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

// Mount app
app.mount('#app')
