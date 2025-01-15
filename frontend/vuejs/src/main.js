import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Import global styles
import '@/shared/assets/styles/styles.css'

// Import Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { 
  faKeyboard, faBolt, faCode, faPencilAlt, 
  faMagic, faSlidersH, faRocket, faStore, 
  faBriefcase, faUsers, faChartLine, faArrowRight,
  faSignOutAlt, faUser, faCog
} from '@fortawesome/free-solid-svg-icons'

// Add icons to library
library.add(
  faKeyboard, faBolt, faCode, faPencilAlt,
  faMagic, faSlidersH, faRocket, faStore,
  faBriefcase, faUsers, faChartLine, faArrowRight,
  faSignOutAlt, faUser, faCog
)

// Configure axios
import axios from 'axios'
import config from '@/shared/config'

// Set base URL for API requests
axios.defaults.baseURL = config.apiUrl

// Add CSRF token to all axios requests
axios.defaults.withCredentials = true
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

// Create Vue app instance
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)

// Register global components
app.component('font-awesome-icon', FontAwesomeIcon)

// Mount app
app.mount('#app')
