import routes from './routes'

export { routes }

// Export any additional router configuration, guards, or utilities here
export const beforeEnter = (to, from, next) => {
  // Add any route guards specific to the home app
  next()
} 