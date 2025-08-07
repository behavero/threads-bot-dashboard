import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Threadly - Threads Bot Dashboard',
  description: 'Manage your Threads accounts and schedule posts',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        {children}
      </body>
    </html>
  )
} 