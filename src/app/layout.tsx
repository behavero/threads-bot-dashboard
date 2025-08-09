import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import BackgroundCanvas from '@/components/layout/BackgroundCanvas'
import AppNav from '@/components/layout/AppNav'
import CapabilityBanner from '@/components/ui/CapabilityBanner'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'Threadly - Threads Bot Dashboard',
  description: 'Automated Threads posting with liquid glass design',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        <BackgroundCanvas />
        <div className="relative min-h-screen">
          <AppNav />
          <CapabilityBanner />
          <main className="content-container py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
} 