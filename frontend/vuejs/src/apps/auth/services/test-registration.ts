/**
 * Test script for registration flow to validate CSRF token handling fixes
 * This script can be used to test the registration process in different environments
 */

import { AuthAPI } from './api'
import type { UserRegistrationData } from '@/apps/auth/types/auth'

export async function testRegistrationFlow(testUserData: UserRegistrationData) {
  console.log('🧪 Starting registration flow test...')
  
  try {
    // Test 1: CSRF Token Fetch
    console.log('🔑 Testing CSRF token fetch...')
    try {
      await AuthAPI.getCSRFToken()
      console.log('✅ CSRF token fetch successful')
    } catch (error) {
      console.warn('⚠️ CSRF token fetch failed:', error)
    }
    
    // Test 2: CSRF Token Ensure
    console.log('🔑 Testing CSRF token ensure...')
    const csrfToken = await AuthAPI.ensureCSRFToken()
    console.log('✅ CSRF token ensure result:', !!csrfToken)
    
    // Test 3: Registration
    console.log('🔄 Testing registration...')
    const result = await AuthAPI.register(testUserData)
    console.log('✅ Registration successful:', result)
    
    return {
      success: true,
      result
    }
    
  } catch (error) {
    console.error('❌ Registration test failed:', error)
    return {
      success: false,
      error
    }
  }
}

// Example usage (commented out to prevent accidental execution)
/*
const testUser: UserRegistrationData = {
  username: 'testuser_' + Date.now(),
  email: 'test_' + Date.now() + '@example.com',
  password: 'TestPassword123!',
  password_confirmation: 'TestPassword123!',
  terms_accepted: true
}

testRegistrationFlow(testUser).then(result => {
  console.log('Test result:', result)
})
*/ 