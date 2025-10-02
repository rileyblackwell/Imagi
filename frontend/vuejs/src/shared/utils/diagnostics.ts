/**
 * Diagnostic utilities for debugging API connectivity issues
 * Especially useful for Railway deployment debugging
 */

export interface DiagnosticResult {
  name: string
  status: 'pass' | 'fail' | 'warning'
  message: string
  details?: any
}

export interface SystemDiagnostics {
  timestamp: string
  environment: string
  results: DiagnosticResult[]
  summary: {
    total: number
    passed: number
    failed: number
    warnings: number
  }
}

/**
 * Run comprehensive system diagnostics
 */
export async function runSystemDiagnostics(): Promise<SystemDiagnostics> {
  const results: DiagnosticResult[] = []
  
  // 1. Check browser connectivity
  results.push({
    name: 'Browser Online Status',
    status: navigator.onLine ? 'pass' : 'fail',
    message: navigator.onLine ? 'Browser reports online' : 'Browser reports offline',
    details: { online: navigator.onLine }
  })
  
  // 2. Check environment configuration
  const isProd = import.meta.env.PROD
  const baseURL = import.meta.env.VITE_BACKEND_URL || ''
  
  results.push({
    name: 'Environment Configuration',
    status: 'pass',
    message: `Running in ${isProd ? 'production' : 'development'} mode`,
    details: {
      isProd,
      mode: import.meta.env.MODE,
      baseURL: baseURL || 'relative URLs',
      backendUrl: import.meta.env.BACKEND_URL || 'not set (browser-side)',
      viteBackendUrl: import.meta.env.VITE_BACKEND_URL || 'not set'
    }
  })
  
  // 3. Check current location
  results.push({
    name: 'Current Location',
    status: 'pass',
    message: `Loaded from ${window.location.origin}`,
    details: {
      href: window.location.href,
      origin: window.location.origin,
      protocol: window.location.protocol,
      host: window.location.host,
      pathname: window.location.pathname
    }
  })
  
  // 4. Check local storage
  try {
    const token = localStorage.getItem('token')
    results.push({
      name: 'Local Storage Access',
      status: 'pass',
      message: 'Can access localStorage',
      details: {
        hasToken: !!token,
        tokenPreview: token ? `${token.substring(0, 20)}...` : 'none'
      }
    })
  } catch (error: any) {
    results.push({
      name: 'Local Storage Access',
      status: 'fail',
      message: 'Cannot access localStorage',
      details: { error: error.message }
    })
  }
  
  // 5. Check cookies
  results.push({
    name: 'Cookie Access',
    status: document.cookie !== undefined ? 'pass' : 'fail',
    message: document.cookie !== undefined ? 'Can access cookies' : 'Cannot access cookies',
    details: {
      cookieCount: document.cookie ? document.cookie.split(';').length : 0,
      hasCsrfToken: document.cookie.includes('csrftoken')
    }
  })
  
  // 6. Test frontend health endpoint (if in production)
  if (isProd) {
    try {
      const response = await fetch('/health', { method: 'GET' })
      const data = await response.json()
      results.push({
        name: 'Frontend Health Check',
        status: response.ok ? 'pass' : 'fail',
        message: response.ok ? 'Frontend Nginx is responding' : 'Frontend Nginx health check failed',
        details: {
          status: response.status,
          data
        }
      })
    } catch (error: any) {
      results.push({
        name: 'Frontend Health Check',
        status: 'fail',
        message: 'Cannot reach frontend health endpoint',
        details: { error: error.message }
      })
    }
  }
  
  // 7. Test backend health endpoint through proxy
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 10000)
    
    const response = await fetch('/api/v1/auth/health/', {
      method: 'GET',
      headers: {
        'X-Request-Type': 'diagnostic-health-check',
        'Accept': 'application/json'
      },
      signal: controller.signal
    })
    
    clearTimeout(timeoutId)
    
    const contentType = response.headers.get('content-type') || ''
    const isJson = contentType.includes('application/json')
    
    let data: any
    try {
      data = await response.json()
    } catch {
      data = await response.text()
    }
    
    if (!response.ok) {
      results.push({
        name: 'Backend Health Check',
        status: 'fail',
        message: `Backend returned ${response.status} ${response.statusText}`,
        details: {
          status: response.status,
          statusText: response.statusText,
          contentType,
          isJson,
          data
        }
      })
    } else if (!isJson) {
      results.push({
        name: 'Backend Health Check',
        status: 'warning',
        message: 'Backend responded but returned non-JSON content',
        details: {
          status: response.status,
          contentType,
          dataPreview: typeof data === 'string' ? data.substring(0, 200) : data
        }
      })
    } else {
      results.push({
        name: 'Backend Health Check',
        status: 'pass',
        message: 'Backend is responding correctly',
        details: {
          status: response.status,
          data
        }
      })
    }
  } catch (error: any) {
    const isTimeout = error.name === 'AbortError'
    results.push({
      name: 'Backend Health Check',
      status: 'fail',
      message: isTimeout ? 'Backend health check timed out after 10s' : 'Cannot reach backend through proxy',
      details: {
        error: error.message,
        errorName: error.name,
        isTimeout,
        possibleCauses: [
          'Backend service is not running',
          'Nginx proxy_pass misconfiguration',
          'Railway private network connectivity issue',
          'Backend not listening on correct port',
          'BACKEND_URL environment variable not set correctly'
        ]
      }
    })
  }
  
  // Calculate summary
  const summary = {
    total: results.length,
    passed: results.filter(r => r.status === 'pass').length,
    failed: results.filter(r => r.status === 'fail').length,
    warnings: results.filter(r => r.status === 'warning').length
  }
  
  return {
    timestamp: new Date().toISOString(),
    environment: isProd ? 'production' : 'development',
    results,
    summary
  }
}

/**
 * Print diagnostics to console in a formatted way
 */
export function printDiagnostics(diagnostics: SystemDiagnostics): void {
  console.group('🔍 System Diagnostics Report')
  console.log(`Timestamp: ${diagnostics.timestamp}`)
  console.log(`Environment: ${diagnostics.environment}`)
  console.log(`Summary: ${diagnostics.summary.passed}/${diagnostics.summary.total} passed, ${diagnostics.summary.failed} failed, ${diagnostics.summary.warnings} warnings`)
  console.log('')
  
  diagnostics.results.forEach((result, index) => {
    const icon = result.status === 'pass' ? '✅' : result.status === 'fail' ? '❌' : '⚠️'
    console.group(`${icon} ${index + 1}. ${result.name}`)
    console.log(`Status: ${result.status}`)
    console.log(`Message: ${result.message}`)
    if (result.details) {
      console.log('Details:', result.details)
    }
    console.groupEnd()
  })
  
  console.groupEnd()
}

/**
 * Run diagnostics and print to console
 */
export async function diagnoseSystem(): Promise<SystemDiagnostics> {
  console.log('🏥 Running system diagnostics...')
  const diagnostics = await runSystemDiagnostics()
  printDiagnostics(diagnostics)
  return diagnostics
}
