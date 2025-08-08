'use client'

import Link from 'next/link'
import Image from 'next/image'

export default function DataDeletionPage() {
  return (
    <div className="min-h-screen relative">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse"></div>
        
        {/* Decorative lines */}
        <div className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/30 to-transparent"></div>
        <div className="absolute top-3/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-purple-500/20 to-transparent"></div>
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
                />
              </Link>
            </div>
            
            {/* Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <Link href="/dashboard" className="modern-button px-4 py-2 text-sm">
                Dashboard
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="modern-card p-8">
          <h1 className="text-4xl font-bold mb-6 gradient-text">Data Deletion</h1>
          <p className="text-gray-300 mb-8">Last updated: January 15, 2025</p>
          
          <div className="space-y-6 text-gray-200">
            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">Your Data Rights</h2>
              <p className="mb-4">
                You have the right to request deletion of your data associated with Threadly at any time. 
                We are committed to protecting your privacy and will process your deletion request promptly.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">How to Request Data Deletion</h2>
              <div className="space-y-4">
                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-white mb-3">Option 1: Through Meta Platforms</h3>
                  <p className="mb-4">
                    If you authenticated via Facebook, Instagram, or Threads, you can submit a deletion request directly from your account settings:
                  </p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>Go to your Facebook/Instagram/Threads account settings</li>
                    <li>Navigate to "Apps and Websites" or "Connected Apps"</li>
                    <li>Find "Threadly" in your connected apps</li>
                    <li>Click "Remove" or "Delete Data"</li>
                  </ul>
                </div>

                <div className="bg-gray-800/50 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-white mb-3">Option 2: Direct API Request</h3>
                  <p className="mb-4">
                    You can also request deletion through our API endpoint:
                  </p>
                  <div className="bg-gray-900/50 p-4 rounded-lg font-mono text-sm">
                    <code className="text-purple-400">POST /api/data-deletion</code>
                  </div>
                  <p className="mt-4 text-sm text-gray-300">
                    Include your <strong>signed_request</strong> from Meta. We will validate the request and remove your data.
                  </p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">What Gets Deleted</h2>
              <p className="mb-4">
                When you request data deletion, we will remove the following information:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Your Threads/Instagram account credentials and session data</li>
                <li>All uploaded captions and images</li>
                <li>Posting history and scheduling data</li>
                <li>Account settings and preferences</li>
                <li>Analytics and engagement data</li>
                <li>Any stored session files</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">Deletion Process</h2>
              <ol className="list-decimal list-inside space-y-3 ml-4">
                <li>
                  <strong>Submit Request:</strong> Use one of the methods above to request deletion
                </li>
                <li>
                  <strong>Verification:</strong> We verify your identity using Meta's signed request
                </li>
                <li>
                  <strong>Processing:</strong> Your data is queued for deletion (usually within 24 hours)
                </li>
                <li>
                  <strong>Confirmation:</strong> You receive a status URL to track deletion progress
                </li>
                <li>
                  <strong>Completion:</strong> All your data is permanently removed from our systems
                </li>
              </ol>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">Status Tracking</h2>
              <p className="mb-4">
                After submitting your deletion request, you will receive a status URL where you can check the progress of your data deletion. 
                The status will show one of the following states:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-yellow-600/20 p-4 rounded-lg border border-yellow-500/30">
                  <h4 className="font-semibold text-yellow-400 mb-2">Pending</h4>
                  <p className="text-sm text-gray-300">Your request is being processed</p>
                </div>
                <div className="bg-blue-600/20 p-4 rounded-lg border border-blue-500/30">
                  <h4 className="font-semibold text-blue-400 mb-2">In Progress</h4>
                  <p className="text-sm text-gray-300">Data deletion is currently running</p>
                </div>
                <div className="bg-green-600/20 p-4 rounded-lg border border-green-500/30">
                  <h4 className="font-semibold text-green-400 mb-2">Completed</h4>
                  <p className="text-sm text-gray-300">All data has been successfully deleted</p>
                </div>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">Contact Us</h2>
              <p className="mb-4">
                If you have any questions about data deletion or need assistance with your request, please contact us:
              </p>
              <div className="bg-gray-800/50 p-4 rounded-lg">
                <p className="text-gray-300">
                  <strong>Email:</strong> support@threadly.com<br />
                  <strong>Subject:</strong> Data Deletion Request<br />
                  <strong>Response Time:</strong> Within 24 hours
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">Important Notes</h2>
              <div className="space-y-3">
                <div className="bg-blue-600/20 p-4 rounded-lg border border-blue-500/30">
                  <h4 className="font-semibold text-blue-400 mb-2">⚠️ Irreversible Action</h4>
                  <p className="text-sm text-gray-300">
                    Data deletion is permanent and cannot be undone. Please ensure you have backed up any important information before requesting deletion.
                  </p>
                </div>
                <div className="bg-purple-600/20 p-4 rounded-lg border border-purple-500/30">
                  <h4 className="font-semibold text-purple-400 mb-2">📋 Legal Compliance</h4>
                  <p className="text-sm text-gray-300">
                    We process deletion requests in compliance with GDPR, CCPA, and other applicable privacy laws.
                  </p>
                </div>
                <div className="bg-green-600/20 p-4 rounded-lg border border-green-500/30">
                  <h4 className="font-semibold text-green-400 mb-2">🔒 Secure Process</h4>
                  <p className="text-sm text-gray-300">
                    All deletion requests are verified using Meta's secure signed_request system to ensure only authorized users can delete their data.
                  </p>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-gray-700 py-4 text-center text-sm text-gray-400 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <a href="/privacy" className="hover:underline text-purple-400">Privacy Policy</a>
          {' '}•{' '}
          <a href="/terms" className="hover:underline text-purple-400">Terms of Service</a>
          {' '}•{' '}
          <a href="/data-deletion" className="hover:underline text-purple-400">Data Deletion</a>
          {' '}•{' '}
          <span>© 2025 Threadly. All rights reserved.</span>
        </div>
      </footer>
    </div>
  )
}
