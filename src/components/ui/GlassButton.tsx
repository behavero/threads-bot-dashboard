'use client'

import { forwardRef, ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface GlassButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  children: ReactNode
  className?: string
  loading?: boolean
  responsive?: boolean
}

const GlassButton = forwardRef<HTMLButtonElement, GlassButtonProps>(
  ({ 
    variant = 'primary', 
    size = 'md', 
    children, 
    className, 
    loading = false,
    responsive = false,
    disabled,
    ...props 
  }, ref) => {
    const baseClasses = 'glass-button'
    
    const variantClasses = {
      primary: 'glass-button-primary',
      ghost: 'glass-button-ghost', 
      danger: 'glass-button-danger'
    }
    
    const sizeClasses = {
      sm: 'h-9 px-4 text-xs',
      md: 'h-11 px-5 text-sm',
      lg: 'h-12 px-6 text-base'
    }
    
    return (
      <button
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          sizeClasses[size],
          responsive && 'button-responsive',
          (disabled || loading) && 'opacity-50 cursor-not-allowed hover:shadow-none',
          loading && 'pointer-events-none',
          className
        )}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        )}
        
        <span className={cn(
          'flex items-center gap-2',
          loading && 'opacity-0'
        )}>
          {children}
        </span>
      </button>
    )
  }
)

GlassButton.displayName = 'GlassButton'

export default GlassButton
