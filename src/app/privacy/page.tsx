'use client'

import Link from 'next/link'
import Image from 'next/image'

export default function PrivacyPage() {
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
          <h1 className="text-4xl font-bold mb-6 gradient-text">Privacy Policy</h1>
          <p className="text-gray-300 mb-8">Last updated: January 15, 2025</p>
          
          <div className="space-y-6 text-gray-200">
            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">1. Information We Collect</h2>
              <p className="mb-4">
                When you use Threadly, we collect information necessary to provide our services:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Account credentials for your Threads/Instagram accounts</li>
                <li>Content you upload (captions, images) for posting</li>
                <li>Usage data to improve our services</li>
                <li>Session information to maintain your login status</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">2. How We Use Your Information</h2>
              <p className="mb-4">
                We use your information solely to provide and improve our Threads management services:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Authenticate and connect to your Threads accounts</li>
                <li>Schedule and post content on your behalf</li>
                <li>Store your content securely for future use</li>
                <li>Provide customer support and service improvements</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">3. Data Protection</h2>
              <p className="mb-4">
                We implement industry-standard security measures to protect your data:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>End-to-end encryption for sensitive data</li>
                <li>Secure session management</li>
                <li>Regular security audits and updates</li>
                <li>Limited access to authorized personnel only</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">4. Data Sharing</h2>
              <p className="mb-4">
                We do not sell, trade, or rent your personal information to third parties. We may share data only in these limited circumstances:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>With your explicit consent</li>
                <li>To comply with legal obligations</li>
                <li>To protect our rights and safety</li>
                <li>With trusted service providers who assist in our operations</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">5. Your Rights</h2>
              <p className="mb-4">
                You have the right to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Access your personal data</li>
                <li>Request correction of inaccurate data</li>
                <li>Request deletion of your data</li>
                <li>Withdraw consent at any time</li>
                <li>Export your data in a portable format</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">6. Contact Us</h2>
              <p className="mb-4">
                If you have any questions about this Privacy Policy or our data practices, please contact us:
              </p>
              <div className="bg-gray-800/50 p-4 rounded-lg">
                <p className="text-gray-300">
                  <strong>Email:</strong> support@threadly.com<br />
                  <strong>Address:</strong> Threadly Inc., 123 Tech Street, San Francisco, CA 94105
                </p>
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
          <span>© 2025 Threadly. All rights reserved.</span>
        </div>
      </footer>
    </div>
  )
}
