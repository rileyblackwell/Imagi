const config = {
  // API Configuration
  apiUrl: (() => {
    // In production, always use relative URLs for browser requests
    // This ensures all API requests go through our Nginx proxy
    const isProd = import.meta.env.PROD || import.meta.env.VITE_APP_ENV === 'production'
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
    
    // If in production, always use relative URL regardless of backend URL config
    if (isProd) {
      console.log('📡 Using relative API URL for production environment')
      return '/api'
    }
    
    // Otherwise use the configured backend URL (for development)
    return backendUrl
  })(),
  
  // Authentication Configuration
  auth: {
    tokenKey: 'token',
    refreshTokenKey: 'refreshToken',
    tokenType: 'Bearer'
  },
  
  // App Configuration
  app: {
    name: 'Imagi',
    description: 'Natural language to code platform',
    version: '1.0.0'
  },

  // Payment Configuration
  payments: {
    stripePublishableKey: import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '',
    creditsPerDollar: 10
  },
  
  // Feature Flags
  features: {
    enablePasswordReset: true,
    enableSocialAuth: false,
    enableTwoFactorAuth: false
  }
}

export default config 