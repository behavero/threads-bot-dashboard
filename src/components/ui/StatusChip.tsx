'use client'

import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface StatusChipProps {
  status: 'success' | 'warning' | 'error' | 'info'
  children: ReactNode
  className?: string
  dot?: boolean
  icon?: ReactNode
}

const StatusChip = ({ status, children, className, dot = true, icon }: StatusChipProps) => {
  const statusClasses = {
    success: 'status-chip-success',
    warning: 'status-chip-warning', 
    error: 'status-chip-error',
    info: 'status-chip-info'
  }
  
  const dotColors = {
    success: 'bg-emerald-400',
    warning: 'bg-amber-400',
    error: 'bg-red-400', 
    info: 'bg-blue-400'
  }
  
  return (
    <span className={cn(statusClasses[status], className)}>
      {icon || (dot && (
        <span className={cn(
          'w-2 h-2 rounded-full flex-shrink-0',
          dotColors[status]
        )} />
      ))}
      <span className="truncate">
        {children}
      </span>
    </span>
  )
}

export default StatusChip
