'use client'

import { useState, useEffect } from 'react'

export default function TestPage() {
  const [testResults, setTestResults] = useState<any>({})
  const [isLoading, setIsLoading] = useState(false)

  const runTests = async () => {
    setIsLoading(true)
    const results: any = {}

    try {
      // Test 1: Backend connection
      try {
        const backendResponse = await fetch('https://threads-bot-dashboard-3.onrender.com/api/status')
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

      // Test 2: Captions API
      try {
        const captionsResponse = await fetch('https://threads-bot-dashboard-3.onrender.com/api/captions')
        const captionsData = await captionsResponse.json()
        results.captions = {
          status: captionsResponse.ok ? '✅ Working' : '❌ Failed',
          data: captionsData
        }
      } catch (error) {
        results.captions = {
          status: '❌ Error',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }

      // Test 3: Accounts API
      try {
        const accountsResponse = await fetch('https://threads-bot-dashboard-3.onrender.com/api/accounts')
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

      // Test 4: Images API
      try {
        const imagesResponse = await fetch('https://threads-bot-dashboard-3.onrender.com/api/images')
        const imagesData = await imagesResponse.json()
        results.images = {
          status: imagesResponse.ok ? '✅ Working' : '❌ Failed',
          data: imagesData
        }
      } catch (error) {
        results.images = {
          status: '❌ Error',
          error: error instanceof Error ? error.message : 'Unknown error'
        }
      }

    } catch (error) {
      results.error = error instanceof Error ? error.message : 'Unknown error'
    }

    setTestResults(results)
    setIsLoading(false)
  }

  if (isLoading) {
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
          <p className="text-gray-300">Testing backend API connections</p>
        </div>

        <div className="modern-card p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-white">Test Results</h2>
            <button
              onClick={runTests}
              disabled={isLoading}
              className="modern-button px-6 py-3 glow-on-hover"
            >
              {isLoading ? 'Running Tests...' : 'Run Tests'}
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
      </div>
    </div>
  )
} 