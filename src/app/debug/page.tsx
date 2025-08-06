'use client'

import { useEffect, useState } from 'react'
import { useAuth } from '@/lib/auth'
import { useRouter } from 'next/navigation'

export default function DebugPage() {
  const { user, loading, session } = useAuth()
  const router = useRouter()
  const [debugInfo, setDebugInfo] = useState<any>({})

  useEffect(() => {
    const info = {
      user: user ? {
        id: user.id,
        email: user.email,
        created_at: user.created_at
      } : null,
      session: session ? {
        access_token: session.access_token ? 'Present' : 'Missing',
        refresh_token: session.refresh_token ? 'Present' : 'Missing',
        expires_at: session.expires_at
      } : null,
      loading,
      timestamp: new Date().toISOString()
    }
    setDebugInfo(info)
  }, [user, session, loading])

  const handleManualRedirect = () => {
    router.push('/dashboard')
  }

  const handleManualLoginRedirect = () => {
    router.push('/login')
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold gradient-text mb-4">Debug Page</h1>
          <p className="text-gray-300">Checking authentication and redirect issues</p>
        </div>

        <div className="modern-card p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Authentication Status</h2>
          
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-300">Loading:</span>
              <span className={loading ? 'text-yellow-400' : 'text-green-400'}>
                {loading ? 'Yes' : 'No'}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-300">User:</span>
              <span className={user ? 'text-green-400' : 'text-red-400'}>
                {user ? 'Logged In' : 'Not Logged In'}
              </span>
            </div>
            
            <div className="flex justify-between">
              <span className="text-gray-300">Session:</span>
              <span className={session ? 'text-green-400' : 'text-red-400'}>
                {session ? 'Active' : 'No Session'}
              </span>
            </div>
          </div>
        </div>

        <div className="modern-card p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Debug Information</h2>
          <pre className="bg-gray-800 p-4 rounded-lg text-sm text-gray-300 overflow-auto">
            {JSON.stringify(debugInfo, null, 2)}
          </pre>
        </div>

        <div className="modern-card p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Manual Actions</h2>
          
          <div className="flex space-x-4">
            <button
              onClick={handleManualRedirect}
              className="modern-button px-6 py-3 glow-on-hover"
            >
              Go to Dashboard
            </button>
            
            <button
              onClick={handleManualLoginRedirect}
              className="modern-button px-6 py-3 bg-gray-600 hover:bg-gray-700"
            >
              Go to Login
            </button>
          </div>
        </div>

        <div className="modern-card p-8">
          <h2 className="text-2xl font-bold text-white mb-6">Current URL</h2>
          <p className="text-gray-300">{typeof window !== 'undefined' ? window.location.href : 'Server side'}</p>
        </div>
      </div>
    </div>
  )
} 