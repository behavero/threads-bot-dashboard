'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import LoginForm from '@/components/LoginForm'

export default function LoginPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && user) {
      console.log('User authenticated, redirecting to dashboard')
      router.push('/dashboard')
    }
  }, [user, loading, router])

  // Add a manual redirect button for debugging
  const handleManualRedirect = () => {
    console.log('Manual redirect to dashboard')
    router.push('/dashboard')
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto"></div>
          <p className="mt-4 text-gray-300">Redirecting to dashboard...</p>
          <button
            onClick={handleManualRedirect}
            className="mt-4 modern-button px-6 py-3 glow-on-hover"
          >
            Manual Redirect
          </button>
        </div>
      </div>
    )
  }

  return <LoginForm />
} 