'use client'

import { useEffect, useState } from 'react'

const BackgroundCanvas = () => {
  const [mounted, setMounted] = useState(false)

  // Only render on client to avoid hydration issues
  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      {/* Base gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900/20 to-slate-900" />
      
      {/* Animated liquid blobs */}
      <div className="absolute inset-0">
        {/* Blob 1 - Primary color */}
        <div 
          className="liquid-blob-1" 
          style={{
            background: `radial-gradient(circle, rgba(167, 139, 250, 0.4) 0%, rgba(167, 139, 250, 0.1) 40%, transparent 70%)`
          }}
        />
        
        {/* Blob 2 - Accent color */}
        <div 
          className="liquid-blob-2"
          style={{
            background: `radial-gradient(circle, rgba(125, 211, 252, 0.3) 0%, rgba(125, 211, 252, 0.1) 40%, transparent 70%)`
          }}
        />
        
        {/* Additional small floating blobs for depth */}
        <div 
          className="absolute w-64 h-64 top-1/3 right-1/3 rounded-full blur-3xl opacity-20 mix-blend-screen animate-float-slow"
          style={{
            background: `radial-gradient(circle, rgba(99, 102, 241, 0.4) 0%, transparent 70%)`,
            animationDelay: '2s'
          }}
        />
        
        <div 
          className="absolute w-48 h-48 bottom-1/3 left-1/3 rounded-full blur-3xl opacity-25 mix-blend-screen animate-float"
          style={{
            background: `radial-gradient(circle, rgba(236, 72, 153, 0.3) 0%, transparent 70%)`,
            animationDelay: '4s'
          }}
        />
      </div>
      
      {/* Subtle radial gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-radial from-transparent via-transparent to-slate-900/20" />
    </div>
  )
}

export default BackgroundCanvas
