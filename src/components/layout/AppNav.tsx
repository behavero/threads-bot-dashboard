'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { 
  HomeIcon,
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  PhotoIcon,
  Bars3Icon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import StatusChip from '@/components/ui/StatusChip'
import GlassButton from '@/components/ui/GlassButton'
import { API_BASE } from '@/lib/config'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Accounts', href: '/accounts', icon: UserGroupIcon },
  { name: 'Captions', href: '/captions', icon: ChatBubbleLeftRightIcon },
  { name: 'Images', href: '/images', icon: PhotoIcon },
]

const AppNav = () => {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'loading'>('loading')

  // Check backend status
  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/health`, { 
          method: 'GET',
          signal: AbortSignal.timeout(5000) // 5s timeout
        })
        
        if (response.ok) {
          setBackendStatus('connected')
        } else {
          setBackendStatus('disconnected')
        }
      } catch (error) {
        setBackendStatus('disconnected')
      }
    }

    checkBackendStatus()
    // Check every 30 seconds
    const interval = setInterval(checkBackendStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  // Close mobile menu when route changes
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [mobileMenuOpen])

  return (
    <>
      {/* Desktop Navigation */}
      <nav className="sticky top-0 z-40 glass-card border-0 border-b border-glass-border rounded-none backdrop-blur-xl">
        <div className="content-container">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <span className="text-xl font-bold gradient-text">
                Threadly
              </span>
            </div>
            
            {/* Desktop Navigation Links */}
            <div className="hidden md:flex items-center space-x-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon
                
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    className={cn(
                      'nav-pill',
                      isActive ? 'nav-pill-active' : 'hover:bg-glass-100'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                )
              })}
            </div>
            
            {/* Status & Mobile Menu Button */}
            <div className="flex items-center gap-3">
              {/* Backend Status */}
              <StatusChip
                status={backendStatus === 'connected' ? 'success' : backendStatus === 'loading' ? 'info' : 'error'}
                className="hidden sm:flex"
                icon={
                  backendStatus === 'loading' ? (
                    <div className="w-2 h-2 border border-current border-t-transparent rounded-full animate-spin" />
                  ) : backendStatus === 'connected' ? (
                    <CheckCircleIcon className="w-3 h-3" />
                  ) : (
                    <ExclamationTriangleIcon className="w-3 h-3" />
                  )
                }
              >
                Backend: {backendStatus === 'loading' ? 'Checking...' : backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
              </StatusChip>
              
              {/* Mobile menu button */}
              <GlassButton
                variant="ghost"
                size="sm"
                className="md:hidden !w-10 !h-10 !p-0"
                onClick={() => setMobileMenuOpen(true)}
                aria-label="Open menu"
              >
                <Bars3Icon className="w-5 h-5" />
              </GlassButton>
            </div>
          </div>
        </div>
      </nav>

      {/* Mobile Navigation Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={() => setMobileMenuOpen(false)}
          />
          
          {/* Mobile Menu */}
          <div className="absolute inset-y-0 right-0 w-full max-w-xs glass-modal !rounded-none !rounded-l-3xl h-full animate-slide-down">
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-glass-border">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
                    <span className="text-white font-bold text-sm">T</span>
                  </div>
                  <span className="text-xl font-bold gradient-text">
                    Threadly
                  </span>
                </div>
                
                <GlassButton
                  variant="ghost"
                  size="sm"
                  className="!w-10 !h-10 !p-0"
                  onClick={() => setMobileMenuOpen(false)}
                  aria-label="Close menu"
                >
                  <XMarkIcon className="w-5 h-5" />
                </GlassButton>
              </div>
              
              {/* Navigation Links */}
              <div className="flex-1 p-6 space-y-2">
                {navigation.map((item) => {
                  const isActive = pathname === item.href
                  const Icon = item.icon
                  
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-2xl transition-colors',
                        isActive 
                          ? 'bg-glass-200 text-white border border-glass-border' 
                          : 'text-white/80 hover:bg-glass-100 hover:text-white'
                      )}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{item.name}</span>
                    </Link>
                  )
                })}
              </div>
              
              {/* Footer with Status */}
              <div className="p-6 border-t border-glass-border">
                <StatusChip
                  status={backendStatus === 'connected' ? 'success' : backendStatus === 'loading' ? 'info' : 'error'}
                  className="w-full justify-center"
                  icon={
                    backendStatus === 'loading' ? (
                      <div className="w-2 h-2 border border-current border-t-transparent rounded-full animate-spin" />
                    ) : backendStatus === 'connected' ? (
                      <CheckCircleIcon className="w-3 h-3" />
                    ) : (
                      <ExclamationTriangleIcon className="w-3 h-3" />
                    )
                  }
                >
                  Backend: {backendStatus === 'loading' ? 'Checking...' : backendStatus === 'connected' ? 'Connected' : 'Disconnected'}
                </StatusChip>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default AppNav
