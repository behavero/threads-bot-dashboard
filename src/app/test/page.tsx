'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'

export default function TestPage() {
  const { user, loading } = useAuth()
  const [testResults, setTestResults] = useState<any>({})
  const [isTesting, setIsTesting] = useState(false)

  const runTests = async () => {
    setIsTesting(true)
    const results: any = {}

    try {
      // Test 1: Authentication
      results.auth = {
        user: user ? '✅ Logged in' : '❌ Not logged in',
        email: user?.email || 'N/A'
      }

      // Test 2: Backend connection
      try {
        const backendResponse = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/status`)
        const backendData = await backendResponse.json()
        results.backend = {
          status: backendResponse.ok ? '✅ Connected' : '❌ Failed',
          data: backendData
        }
      } catch (error) {
        results.backend = {
          status: '❌ Error',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }

      // Test 3: Supabase connection
      try {
        const supabaseResponse = await fetch('/api/test-env')
        const supabaseData = await supabaseResponse.json()
        results.supabase = {
          status: supabaseResponse.ok ? '✅ Connected' : '❌ Failed',
          data: supabaseData
        }
      } catch (error) {
        results.supabase = {
          status: '❌ Error',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }

      // Test 4: Accounts API
      try {
        const accountsResponse = await fetch('/api/accounts')
        const accountsData = await accountsResponse.json()
        results.accounts = {
          status: accountsResponse.ok ? '✅ Working' : '❌ Failed',
          data: accountsData
        }
      } catch (error) {
        results.accounts = {
          status: '❌ Error',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }

      // Test 5: Prompts API
      try {
        const promptsResponse = await fetch('/api/prompts')
        const promptsData = await promptsResponse.json()
        results.prompts = {
          status: promptsResponse.ok ? '✅ Working' : '❌ Failed',
          data: promptsData
        }
      } catch (error) {
        results.prompts = {
          status: '❌ Error',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }

    } catch (error) {
      results.error = error instanceof Error ? error.message : 'Unknown error'
    }

    setTestResults(results)
    setIsTesting(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold gradient-text mb-4">System Test Page</h1>
          <p className="text-gray-300">Testing authentication and API connections</p>
        </div>

        <div className="modern-card p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Test Results</h2>
            <button
              onClick={runTests}
              disabled={isTesting}
              className="modern-button px-6 py-3 glow-on-hover"
            >
              {isTesting ? 'Running Tests...' : 'Run Tests'}
            </button>
          </div>

          {Object.keys(testResults).length > 0 && (
            <div className="space-y-6">
              {Object.entries(testResults).map(([key, value]: [string, any]) => (
                <div key={key} className="modern-card p-4">
                  <h3 className="text-lg font-semibold text-white mb-2 capitalize">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </h3>
                  <div className="space-y-2">
                    {typeof value === 'object' ? (
                      Object.entries(value).map(([subKey, subValue]: [string, any]) => (
                        <div key={subKey} className="flex justify-between">
                          <span className="text-gray-300">{subKey}:</span>
                          <span className="text-white">{String(subValue)}</span>
                        </div>
                      ))
                    ) : (
                      <span className="text-white">{String(value)}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="modern-card p-8">
          <h2 className="text-2xl font-bold text-white mb-4">Current Status</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-300">Authentication:</span>
              <span className={user ? 'text-green-400' : 'text-red-400'}>
                {user ? '✅ Logged In' : '❌ Not Logged In'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">User Email:</span>
              <span className="text-white">{user?.email || 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-300">User ID:</span>
              <span className="text-white">{user?.id || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
} 