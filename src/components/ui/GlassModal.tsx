'use client'

import { Fragment, ReactNode, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { cn } from '@/lib/utils'
import { XMarkIcon } from '@heroicons/react/24/outline'
import GlassButton from './GlassButton'

interface GlassModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  className?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  fullScreenOnMobile?: boolean
}

const GlassModal = ({ 
  isOpen, 
  onClose, 
  title, 
  children, 
  className,
  size = 'md',
  fullScreenOnMobile = true
}: GlassModalProps) => {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Prevent body scroll
      document.body.style.overflow = 'hidden'
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])
  
  if (!isOpen) return null
  
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg', 
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  }
  
  const modalContent = (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? 'modal-title' : undefined}
    >
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      
      {/* Modal */}
      <div className={cn(
        'glass-modal w-full animate-slide-up relative',
        sizeClasses[size],
        fullScreenOnMobile && 'sm:rounded-3xl rounded-none sm:m-4 m-0 sm:h-auto h-full sm:max-h-[90vh] overflow-y-auto',
        !fullScreenOnMobile && 'rounded-3xl max-h-[90vh] overflow-y-auto',
        className
      )}>
        {/* Header */}
        {title && (
          <div className="flex items-center justify-between mb-6">
            <h2 id="modal-title" className="heading-4 text-white">
              {title}
            </h2>
            <GlassButton
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="!h-9 !w-9 !p-0 hover:bg-white/10"
              aria-label="Close modal"
            >
              <XMarkIcon className="w-5 h-5" />
            </GlassButton>
          </div>
        )}
        
        {!title && (
          <div className="absolute top-4 right-4">
            <GlassButton
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="!h-9 !w-9 !p-0 hover:bg-white/10"
              aria-label="Close modal"
            >
              <XMarkIcon className="w-5 h-5" />
            </GlassButton>
          </div>
        )}
        
        {/* Content */}
        <div className={cn(!title && 'pt-12')}>
          {children}
        </div>
      </div>
    </div>
  )
  
  // Use portal to render at document level
  return typeof document !== 'undefined' 
    ? createPortal(modalContent, document.body)
    : null
}

export default GlassModal
