'use client'

import { useState, useEffect } from 'react'
import { ExclamationTriangleIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { fetchConfigStatus, type ConfigStatus } from '@/lib/api/client'
import GlassButton from './GlassButton'

export default function CapabilityBanner() {
  const [config, setConfig] = useState<ConfigStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [dismissed, setDismissed] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadConfig = async () => {
      try {
        setLoading(true)
        const configStatus = await fetchConfigStatus()
        setConfig(configStatus)
      } catch (err) {
        console.error('Failed to load config status:', err)
        setError(err instanceof Error ? err.message : 'Failed to load config')
      } finally {
        setLoading(false)
      }
    }

    loadConfig()
  }, [])

  // Don't show banner if dismissed, loading, error, or publishing is enabled
  if (dismissed || loading || error || !config || config.publishEnabled) {
    return null
  }

  // Only show if OAuth is configured but publishing is disabled
  if (!config.oauthConfigured) {
    return null
  }

  return (
    <div className="sticky top-0 z-50 backdrop-blur-xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-b border-amber-400/20">
      <div className="content-container py-3">
        <div className="flex items-center gap-3">
          <ExclamationTriangleIcon className="w-5 h-5 text-amber-400 flex-shrink-0" />
          
          <div className="flex-1 text-sm">
            <p className="text-amber-100">
              <span className="font-medium">Connected to Threads.</span> Publishing is disabled until Meta approves content_publish scope. 
              Autopilot will queue content and post automatically once approved.
            </p>
            {config.scopes && (
              <p className="text-amber-200/80 text-xs mt-1">
                Current scopes: {config.scopes.join(', ')}
              </p>
            )}
          </div>
          
          <GlassButton
            variant="ghost"
            size="sm"
            onClick={() => setDismissed(true)}
            className="text-amber-300 hover:text-amber-100 p-1"
          >
            <XMarkIcon className="w-4 h-4" />
          </GlassButton>
        </div>
      </div>
    </div>
  )
}
