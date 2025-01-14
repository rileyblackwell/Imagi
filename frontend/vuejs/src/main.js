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
  faBriefcase, faUsers, faChartLine, faArrowRight 
} from '@fortawesome/free-solid-svg-icons'

// Add icons to library
library.add(
  faKeyboard, faBolt, faCode, faPencilAlt,
  faMagic, faSlidersH, faRocket, faStore,
  faBriefcase, faUsers, faChartLine, faArrowRight
)

// Configure axios for CSRF
import axios from 'axios'

// Get CSRF token from cookie
function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

// Add CSRF token to all axios requests
axios.defaults.headers.common['X-CSRFToken'] = getCookie('csrftoken')
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'
axios.defaults.withCredentials = true

// Create Vue app and Pinia instance
const app = createApp(App)
const pinia = createPinia()

// Register Font Awesome component
app.component('font-awesome-icon', FontAwesomeIcon)

// Use plugins
app.use(pinia)
app.use(router)

// Mount app
app.mount('#app')
