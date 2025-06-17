/**
 * Railway Debug Utilities
 * Helper functions to diagnose Railway networking issues
 */

export class RailwayDebugger {
  private static instance: RailwayDebugger
  
  public static getInstance(): RailwayDebugger {
    if (!RailwayDebugger.instance) {
      RailwayDebugger.instance = new RailwayDebugger()
    }
    return RailwayDebugger.instance
  }

  /**
   * Print comprehensive environment debug information
   */
  public debugEnvironment(): void {
    console.log('🚂 Railway Environment Debug Information')
    console.log('=====================================')
    console.log('Environment Variables:')
    console.log('  NODE_ENV:', import.meta.env.NODE_ENV)
    console.log('  PROD:', import.meta.env.PROD)
    console.log('  DEV:', import.meta.env.DEV)
    console.log('  VITE_BACKEND_URL:', import.meta.env.VITE_BACKEND_URL)
    console.log('')
    
    console.log('Frontend Details:')
    console.log('  Current URL:', window.location.href)
    console.log('  Origin:', window.location.origin)
    console.log('  Host:', window.location.host)
    console.log('  Protocol:', window.location.protocol)
    console.log('')
    
    console.log('Expected Railway Services:')
    console.log('  Frontend: http://frontend.railway.internal:80')
    console.log('  Backend: http://backend.railway.internal:8000')
    console.log('')
  }

  /**
   * Test basic connectivity to backend health endpoint
   */
  public async testBackendConnectivity(): Promise<void> {
    console.log('🔍 Testing Backend Connectivity...')
    
    const endpoints = [
      '/backend-health',
      '/api/v1/auth/health/',
      '/health'
    ]
    
    for (const endpoint of endpoints) {
      try {
        console.log(`Testing ${endpoint}...`)
        const response = await fetch(endpoint, {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
            'X-Test-Request': 'railway-debug'
          }
        })
        
        console.log(`✅ ${endpoint}: ${response.status}`)
        const data = await response.json()
        console.log(`  Data:`, data)
      } catch (error: any) {
        console.log(`❌ ${endpoint}: ${error.message}`)
      }
    }
  }

  /**
   * Test CSRF token endpoint specifically
   */
  public async testCSRFEndpoint(): Promise<void> {
    console.log('🔑 Testing CSRF Token Endpoint...')
    
    const csrfUrl = '/api/v1/auth/csrf/'
    
    try {
      console.log(`Making request to: ${csrfUrl}`)
      const response = await fetch(csrfUrl, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'X-Test-Request': 'csrf-debug',
          'X-Frontend-Service': 'vue-frontend'
        }
      })
      
      console.log(`✅ CSRF endpoint: ${response.status}`)
      
      // Convert headers to object for logging
      const headers: Record<string, string> = {}
      response.headers.forEach((value, key) => {
        headers[key] = value
      })
      console.log('Response headers:', headers)
      
      const data = await response.json()
      console.log('Response data:', data)
      
      // Check cookies
      console.log('Cookies after request:', document.cookie)
      
    } catch (error: any) {
      console.log(`❌ CSRF endpoint failed: ${error.message}`)
      console.log('Error details:', error)
    }
  }

  /**
   * Test network reachability with different methods
   */
  public async testNetworkReachability(): Promise<void> {
    console.log('🌐 Testing Network Reachability...')
    
    const backendUrl = import.meta.env.VITE_BACKEND_URL
    if (!backendUrl) {
      console.log('⚠️ VITE_BACKEND_URL not set - this is expected if using nginx proxy')
      console.log('ℹ️ In Railway, frontend connects to backend via nginx proxy at relative URLs')
      console.log('ℹ️ If you want direct backend connection, set VITE_BACKEND_URL=http://backend.railway.internal:8000')
      return
    }
    
    console.log(`Testing direct backend URL: ${backendUrl}`)
    
    try {
      // Test direct connection
      const directUrl = `${backendUrl}/api/v1/auth/health/`
      console.log(`Direct test to: ${directUrl}`)
      
      const response = await fetch(directUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'X-Test-Request': 'direct-backend-test'
        }
      })
      
      console.log(`✅ Direct backend connection: ${response.status}`)
      const data = await response.json()
      console.log('Direct response:', data)
      
    } catch (error: any) {
      console.log(`❌ Direct backend connection failed: ${error.message}`)
    }
  }

  /**
   * Run comprehensive Railway debugging
   */
  public async runFullDiagnostics(): Promise<void> {
    console.log('🚂 Starting Railway Full Diagnostics...')
    console.log('==========================================')
    
    this.debugEnvironment()
    await this.testBackendConnectivity()
    await this.testCSRFEndpoint()
    await this.testNetworkReachability()
    
    console.log('🚂 Railway Diagnostics Complete')
    console.log('===============================')
  }
}

// Export convenience function
export const runRailwayDiagnostics = () => {
  return RailwayDebugger.getInstance().runFullDiagnostics()
}

// Make available globally for console debugging
if (typeof window !== 'undefined') {
  (window as any).railwayDebug = RailwayDebugger.getInstance()
} 