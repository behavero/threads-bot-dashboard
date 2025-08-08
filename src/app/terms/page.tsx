'use client'

import Link from 'next/link'
import Image from 'next/image'

export default function TermsPage() {
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
          <h1 className="text-4xl font-bold mb-6 gradient-text">Terms of Service</h1>
          <p className="text-gray-300 mb-8">Last updated: January 15, 2025</p>
          
          <div className="space-y-6 text-gray-200">
            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">1. Acceptance of Terms</h2>
              <p className="mb-4">
                By accessing and using Threadly ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">2. Description of Service</h2>
              <p className="mb-4">
                Threadly is a social media management platform that allows users to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Connect and manage Threads/Instagram accounts</li>
                <li>Schedule and automate posts</li>
                <li>Upload and manage content (captions, images)</li>
                <li>Track engagement and analytics</li>
                <li>Manage multiple accounts from a single dashboard</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">3. User Accounts</h2>
              <p className="mb-4">
                When you create an account with us, you must provide accurate, complete, and current information. You are responsible for:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Maintaining the security of your account credentials</li>
                <li>All activities that occur under your account</li>
                <li>Notifying us immediately of any unauthorized use</li>
                <li>Ensuring your account information remains accurate</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">4. Acceptable Use</h2>
              <p className="mb-4">
                You agree to use the Service only for lawful purposes and in accordance with these Terms. You agree not to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Violate any applicable laws or regulations</li>
                <li>Infringe on intellectual property rights</li>
                <li>Post spam, malicious content, or inappropriate material</li>
                <li>Attempt to gain unauthorized access to our systems</li>
                <li>Use the service for any commercial purpose without permission</li>
                <li>Interfere with or disrupt the service</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">5. Content and Intellectual Property</h2>
              <p className="mb-4">
                You retain ownership of content you upload to our service. By uploading content, you grant us a limited license to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Store and process your content for service delivery</li>
                <li>Display your content as part of the service</li>
                <li>Use your content to provide customer support</li>
                <li>Improve our services (anonymized data only)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">6. Service Availability</h2>
              <p className="mb-4">
                We strive to maintain high service availability but cannot guarantee uninterrupted access. The service may be temporarily unavailable due to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Scheduled maintenance and updates</li>
                <li>Technical issues beyond our control</li>
                <li>Third-party service disruptions (Threads/Instagram API)</li>
                <li>Force majeure events</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">7. Limitation of Liability</h2>
              <p className="mb-4">
                Threadly shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Loss of data or content</li>
                <li>Service interruptions or downtime</li>
                <li>Third-party platform changes affecting our service</li>
                <li>Damages resulting from your use of the service</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">8. Termination</h2>
              <p className="mb-4">
                We may terminate or suspend your account and access to the service at any time, with or without cause, with or without notice. You may terminate your account at any time by contacting support.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">9. Changes to Terms</h2>
              <p className="mb-4">
                We reserve the right to modify these terms at any time. We will notify users of any material changes via email or through the service. Your continued use of the service after changes constitutes acceptance of the new terms.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold mb-4 text-white">10. Contact Information</h2>
              <p className="mb-4">
                If you have any questions about these Terms of Service, please contact us:
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
          <a href="/data-deletion" className="hover:underline text-purple-400">Data Deletion</a>
          {' '}•{' '}
          <span>© 2025 Threadly. All rights reserved.</span>
        </div>
      </footer>
    </div>
  )
}
