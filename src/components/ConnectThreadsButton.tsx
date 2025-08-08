'use client'

import { useState } from 'react'
import { API_ENDPOINTS, META_CONFIG } from '@/lib/config'

interface ConnectThreadsButtonProps {
  accountId: number
  accountUsername: string
  isConnected: boolean
  onConnectionChange?: (accountId: number, connected: boolean) => void
  className?: string
}

export default function ConnectThreadsButton({
  accountId,
  accountUsername,
  isConnected,
  onConnectionChange,
  className = ''
}: ConnectThreadsButtonProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleConnect = async () => {
    if (isLoading) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      // Redirect to backend OAuth start endpoint
      window.location.href = `${API_ENDPOINTS.AUTH_START}?account_id=${accountId}`
      
    } catch (err) {
      console.error('Connect Threads error:', err)
      setError(err instanceof Error ? err.message : 'Failed to connect')
      setIsLoading(false)
    }
  }

  const handleDisconnect = async () => {
    if (isLoading) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_ENDPOINTS.AUTH_REFRESH}?account_id=${accountId}`, {
        method: 'DELETE',
      })
      
      if (response.ok) {
        onConnectionChange?.(accountId, false)
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to disconnect')
      }
      
    } catch (err) {
      console.error('Disconnect error:', err)
      setError(err instanceof Error ? err.message : 'Failed to disconnect')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={`flex flex-col gap-2 ${className}`}>
      {error && (
        <div className="text-red-400 text-sm bg-red-500/10 p-2 rounded">
          {error}
        </div>
      )}
      
      {isConnected ? (
        <button
          onClick={handleDisconnect}
          disabled={isLoading}
          className="modern-button px-4 py-2 text-sm bg-red-600 hover:bg-red-700 disabled:opacity-50"
        >
          {isLoading ? 'Disconnecting...' : 'Disconnect Threads'}
        </button>
      ) : (
        <button
          onClick={handleConnect}
          disabled={isLoading}
          className="modern-button px-4 py-2 text-sm bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
        >
          {isLoading ? 'Connecting...' : 'Connect Threads'}
        </button>
      )}
      
      <div className="text-xs text-gray-400">
        {isConnected ? 'Connected to Threads API' : 'Connect to post via Threads API'}
      </div>
    </div>
  )
}
