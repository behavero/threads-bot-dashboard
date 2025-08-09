import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import BackgroundCanvas from '@/components/layout/BackgroundCanvas'
import AppNav from '@/components/layout/AppNav'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
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
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="font-sans antialiased">
        <BackgroundCanvas />
        <div className="relative min-h-screen">
          <AppNav />
          <main className="content-container py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
} 