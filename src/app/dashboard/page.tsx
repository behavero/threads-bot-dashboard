'use client'

import { useState } from 'react'
import EngagementChart from '@/components/EngagementChart'
import AccountsPage from '@/app/accounts/page'
import CaptionsPage from '@/app/captions/page'
import ImagesPage from '@/app/images/page'
import Link from 'next/link'
import Image from 'next/image'

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const navigationItems = [
    { id: 'dashboard', name: 'Dashboard' },
    { id: 'accounts', name: 'Accounts' },
    { id: 'captions', name: 'Captions' },
    { id: 'schedule', name: 'Schedule' },
    { id: 'images', name: 'Images' },
  ]

  return (
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
                  className="max-h-8 sm:max-h-12 md:max-h-16 h-auto w-auto text-white hover:opacity-90 transition-opacity duration-200 [&_path]:fill-white [&_path]:dark:fill-white"
                  onError={(e) => {
                    console.error('Logo failed to load:', e)
                  }}
                  onLoad={() => {
                    console.log('Logo loaded successfully')
                  }}
                />
              </Link>
            </div>
            
            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <button
                className="modern-button px-4 py-2 text-sm"
              >
                Dashboard
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

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden modern-card absolute top-full left-0 right-0 z-20 mt-2 mx-4">
          <div className="px-4 py-2 space-y-2">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  setActiveTab(item.id)
                  setIsMobileMenuOpen(false)
                }}
                className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                  activeTab === item.id
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-purple-600/20'
                }`}
              >
                {item.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="relative z-10 pt-8 pb-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Desktop Navigation Tabs */}
          <div className="hidden md:flex items-center space-x-8 mb-8">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  activeTab === item.id
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-300 hover:bg-purple-600/20'
                }`}
              >
                {item.name}
              </button>
            ))}
          </div>

          {/* Content Sections */}
          {activeTab === 'dashboard' && <DashboardContent />}
          {activeTab === 'accounts' && <AccountsContent />}
          {activeTab === 'captions' && <CaptionsContent />}
          {activeTab === 'schedule' && <ScheduleContent />}
          {activeTab === 'images' && <ImagesContent />}
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-gray-700 py-4 text-center text-sm text-gray-400 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <a href="/privacy" className="hover:underline text-purple-400">Privacy Policy</a>
          {' '}•{' '}
          <a href="/terms" className="hover:underline text-purple-400">Terms of Service</a>
          {' '}•{' '}
          <span>© 2025 Threadly. All rights reserved.</span>
        </div>
      </footer>
    </div>
  )
}

function DashboardContent() {
  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Global Results Overview */}
      <div className="modern-card p-6 sm:p-12 floating">
        <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-white mb-6 sm:mb-8">
          Global Results
        </h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 items-start">
          {/* Key Metrics */}
          <div className="space-y-6">
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
            
            {/* Traffic & Performance */}
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-800/50 rounded-lg">
                <span className="text-gray-300 text-sm sm:text-base">Success Rate</span>
                <span className="text-green-400 font-bold text-lg">98.5%</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-800/50 rounded-lg">
                <span className="text-gray-300 text-sm sm:text-base">Avg Response Time</span>
                <span className="text-blue-400 font-bold text-lg">2.3s</span>
              </div>
              <div className="flex justify-between items-center p-4 bg-gray-800/50 rounded-lg">
                <span className="text-gray-300 text-sm sm:text-base">Daily Posts</span>
                <span className="text-purple-400 font-bold text-lg">847</span>
              </div>
            </div>
          </div>

          {/* Account Status & Alerts */}
          <div className="space-y-6">
            <div className="modern-card p-4 sm:p-6">
              <h3 className="text-lg sm:text-xl font-bold text-white mb-4">Account Status</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300 text-sm">Healthy Accounts</span>
                  <span className="text-green-400 font-bold">28</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300 text-sm">Warning Accounts</span>
                  <span className="text-yellow-400 font-bold">4</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300 text-sm">Suspended Accounts</span>
                  <span className="text-red-400 font-bold">2</span>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="modern-card p-4 sm:p-6">
              <h3 className="text-lg sm:text-xl font-bold text-white mb-4">Recent Activity</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Last Post</span>
                  <span className="text-white">2 min ago</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Next Scheduled</span>
                  <span className="text-white">15 min</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-300">Queue Status</span>
                  <span className="text-green-400">Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Dashboard Overview */}
      <div className="modern-card p-6 sm:p-8">
        <h3 className="text-xl sm:text-2xl font-bold text-white mb-6 sm:mb-8">
          System Overview
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