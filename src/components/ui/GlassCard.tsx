'use client'

import { forwardRef, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: ReactNode
  className?: string
  title?: string
  subtitle?: string
  actions?: ReactNode
  dense?: boolean
  animate?: boolean
}

const GlassCard = forwardRef<HTMLDivElement, GlassCardProps>(
  ({ children, className, title, subtitle, actions, dense = false, animate = true, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'glass-card p-6',
          dense && 'p-4',
          animate && 'animate-fade-in',
          className
        )}
        {...props}
      >
        {(title || subtitle || actions) && (
          <div className="flex items-start justify-between mb-6">
            <div className="min-w-0 flex-1">
              {title && (
                <h3 className="heading-4 text-white mb-1">
                  {title}
                </h3>
              )}
              {subtitle && (
                <p className="text-caption">
                  {subtitle}
                </p>
              )}
            </div>
            {actions && (
              <div className="flex items-center gap-2 ml-4">
                {actions}
              </div>
            )}
          </div>
        )}
        
        {/* Subtle divider line */}
        {(title || subtitle || actions) && (
          <div className="relative mb-6">
            <div className="absolute inset-0 border-t border-glass-border" />
          </div>
        )}
        
        <div className={cn(
          'space-y-4',
          dense && 'space-y-3'
        )}>
          {children}
        </div>
      </div>
    )
  }
)

GlassCard.displayName = 'GlassCard'

export default GlassCard
