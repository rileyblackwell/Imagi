import { createStore } from 'vuex'
import auth from './modules/auth'
import projects from './modules/projects'

export default createStore({
  modules: {
    auth,
    projects
  }
}) 