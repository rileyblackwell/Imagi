const config = {
  // API Configuration
  apiUrl: (() => {
    const url = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
    // Railway internal URLs require the port to be specified
    return url
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