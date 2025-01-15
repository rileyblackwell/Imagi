const config = {
  // API Configuration
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  
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