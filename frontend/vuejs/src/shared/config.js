const config = {
  // API Configuration
  apiUrl: (() => {
    // In production, use relative URLs instead of Railway internal URLs
    // This allows the Nginx proxy to handle the request properly
    const isProd = import.meta.env.PROD || import.meta.env.VITE_APP_ENV === 'production'
    const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
    
    // If this is a Railway internal URL and we're in production, use relative URL
    if (isProd && backendUrl.includes('railway.internal')) {
      console.log('📡 Using relative API URL for production environment')
      return ''
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