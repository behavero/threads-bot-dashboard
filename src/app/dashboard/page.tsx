'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/auth'
import ProtectedRoute from '@/components/ProtectedRoute'
import EngagementChart from '@/components/EngagementChart'
import AccountsPage from '@/app/accounts/page'
import CaptionsPage from '@/app/captions/page'
import ImagesPage from '@/app/images/page'
import Link from 'next/link'
import Image from 'next/image'

export default function DashboardPage() {
  const { user, signOut } = useAuth()
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const handleSignOut = async () => {
    await signOut()
  }

  const navigationItems = [
    { id: 'dashboard', name: 'Dashboard' },
    { id: 'accounts', name: 'Accounts' },
    { id: 'captions', name: 'Captions' },
    { id: 'schedule', name: 'Schedule' },
    { id: 'images', name: 'Images' },
  ]

  return (
    <ProtectedRoute>
      <div className="min-h-screen relative">
        {/* Background decorative elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
          
          {/* Decorative lines */}
          <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent"></div>
          <div className="absolute top-3/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"></div>
          
          {/* Decorative circles */}
          <div className="absolute top-1/3 right-1/4 w-32 h-32 border border-purple-500/20 rounded-full"></div>
          <div className="absolute bottom-1/3 left-1/4 w-24 h-24 border border-purple-500/15 rounded-full"></div>
          <div className="absolute top-2/3 right-1/3 w-16 h-16 border border-purple-500/25 rounded-full"></div>
        </div>

        {/* Header */}
        <header className="modern-nav relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16 sm:h-20">
              <div className="flex items-center">
                <Link href="/" className="flex items-center">
                  <Image
                    src="/logo.svg"
                    alt="Threadly Logo"
                    width={400}
                    height={80}
                    priority
                    className="max-h-8 sm:max-h-12 md:max-h-16 h-auto w-auto text-white hover:opacity-90 transition-opacity duration-200"
                  />
                </Link>
              </div>
              
              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-6">
                <button
                  onClick={handleSignOut}
                  className="modern-button px-4 py-2 text-sm"
                >
                  Sign Out
                </button>
              </div>

              {/* Mobile Burger Menu Button */}
              <div className="md:hidden">
                <button
                  onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                  className="text-white p-2 rounded-lg hover:bg-purple-600/20 transition-colors"
                  aria-label="Toggle menu"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    {isMobileMenuOpen ? (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    ) : (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 6h16M4 12h16M4 18h16"
                      />
                    )}
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Mobile Navigation Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden modern-nav relative z-10 border-t border-gray-700">
            <div className="px-4 py-2 space-y-1">
              {navigationItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id)
                    setIsMobileMenuOpen(false)
                  }}
                  className={`w-full text-left px-4 py-3 rounded-lg transition-colors ${
                    activeTab === item.id
                      ? 'bg-purple-600/20 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                  }`}
                >
                  {item.name}
                </button>
              ))}
              <div className="border-t border-gray-700 mt-2 pt-2">
                <button
                  onClick={() => {
                    handleSignOut()
                    setIsMobileMenuOpen(false)
                  }}
                  className="w-full text-left px-4 py-3 rounded-lg text-red-400 hover:text-red-300 hover:bg-red-600/20 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Desktop Navigation */}
        <nav className="hidden md:block modern-nav relative z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8">
              {navigationItems.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`nav-link py-6 px-1 font-medium text-sm transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'text-white'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Content */}
        <main className="relative z-10 max-w-7xl mx-auto py-4 sm:py-8 px-4 sm:px-6 lg:px-8">
          {activeTab === 'dashboard' && <DashboardContent />}
          {activeTab === 'accounts' && <AccountsContent />}
          {activeTab === 'captions' && <CaptionsContent />}
          {activeTab === 'schedule' && <ScheduleContent />}
          {activeTab === 'images' && <ImagesContent />}
        </main>
      </div>
    </ProtectedRoute>
  )
}

function DashboardContent() {
  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Hero Section */}
      <div className="modern-card p-6 sm:p-12 floating">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 items-center">
          <div>
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold gradient-text mb-4 sm:mb-6">
              Threads Bot Is a Premier Social Media Automation Platform
            </h2>
            <p className="text-base sm:text-lg text-gray-300 mb-6 sm:mb-8 leading-relaxed">
              Renowned for powering the backbone of social media ecosystems with our state-of-the-art automation services, content scheduling & engagement tracking.
            </p>
            <button className="modern-button px-6 sm:px-8 py-3 sm:py-4 text-base sm:text-lg glow-on-hover w-full sm:w-auto">
              GET STARTED
            </button>
          </div>
          <div className="relative">
            <div className="grid grid-cols-2 gap-4 sm:gap-6">
              <div className="modern-card p-4 sm:p-6 text-center">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold gradient-text mb-2">192k</div>
                <div className="text-xs sm:text-sm text-gray-300">Total Posts</div>
              </div>
              <div className="modern-card p-4 sm:p-6 text-center">
                <div className="text-3xl sm:text-4xl lg:text-5xl font-bold gradient-text mb-2">34</div>
                <div className="text-xs sm:text-sm text-gray-300">Active Accounts</div>
              </div>
            </div>
            
            {/* Connection lines */}
            <div className="absolute top-1/2 left-1/2 w-full h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent transform -translate-y-1/2"></div>
            <div className="absolute top-1/2 left-1/2 w-px h-full bg-gradient-to-b from-transparent via-purple-500/30 to-transparent transform -translate-x-1/2"></div>
          </div>
        </div>
      </div>

      {/* Dashboard Overview */}
      <div className="modern-card p-6 sm:p-8">
        <h3 className="text-xl sm:text-2xl font-bold text-white mb-6 sm:mb-8">
          Dashboard Overview
        </h3>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <div className="modern-card p-4 sm:p-6 text-center hover:scale-105 transition-transform duration-300">
            <div className="text-2xl sm:text-3xl lg:text-4xl font-bold gradient-text mb-2">0</div>
            <div className="text-xs sm:text-sm text-gray-300">Total Accounts</div>
          </div>
          <div className="modern-card p-4 sm:p-6 text-center hover:scale-105 transition-transform duration-300">
            <div className="text-2xl sm:text-3xl lg:text-4xl font-bold gradient-text mb-2">0</div>
            <div className="text-xs sm:text-sm text-gray-300">Active</div>
          </div>
          <div className="modern-card p-4 sm:p-6 text-center hover:scale-105 transition-transform duration-300">
            <div className="text-2xl sm:text-3xl lg:text-4xl font-bold gradient-text mb-2">0</div>
            <div className="text-xs sm:text-sm text-gray-300">Scheduled</div>
          </div>
          <div className="modern-card p-4 sm:p-6 text-center hover:scale-105 transition-transform duration-300">
            <div className="text-2xl sm:text-3xl lg:text-4xl font-bold gradient-text mb-2">0</div>
            <div className="text-xs sm:text-sm text-gray-300">Errors</div>
          </div>
        </div>
      </div>

      {/* Engagement Analytics */}
      <div className="modern-card p-6 sm:p-8">
        <EngagementChart />
      </div>
    </div>
  )
}

function AccountsContent() {
  return <AccountsPage />
}

function CaptionsContent() {
  return <CaptionsPage />
}

function ScheduleContent() {
  return (
    <div className="modern-card p-6 sm:p-8">
      <h3 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6">
        Schedule
      </h3>
      <p className="text-gray-300">No scheduled posts yet.</p>
    </div>
  )
}

function ImagesContent() {
  return <ImagesPage />
} 