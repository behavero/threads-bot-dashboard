'use client'

import { useEffect, useState } from 'react'
import { 
  UserGroupIcon, 
  ChatBubbleLeftRightIcon, 
  PhotoIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PlayIcon,
  CheckCircleIcon,
  TrophyIcon
} from '@heroicons/react/24/outline'
import { API_BASE } from '@/lib/config'
import GlassCard from '@/components/ui/GlassCard'
import GlassButton from '@/components/ui/GlassButton'
import StatusChip from '@/components/ui/StatusChip'

interface DashboardStats {
  accountsConnected: {
    session: number
    official: number
    total: number
  }
  postsToday: number
  pendingDue: number
  lastError: string | null
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [runningTick, setRunningTick] = useState(false)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      // Fetch actual stats from backend
      const [accountsResponse, autopilotResponse] = await Promise.all([
        fetch(`${API_BASE}/api/accounts`),
        fetch(`${API_BASE}/autopilot/status`)
      ])
      
      const accountsData = await accountsResponse.json()
      const autopilotData = await autopilotResponse.json()
      
      if (accountsData.ok && autopilotData.ok) {
        const accounts = accountsData.accounts || []
        const sessionAccounts = accounts.filter((a: any) => a.connection_status === 'connected_session').length
        const officialAccounts = accounts.filter((a: any) => a.connection_status === 'connected_official').length
        
        // Get last error from autopilot status
        const errorDetails = autopilotData.error_details || []
        const lastError = errorDetails.length > 0 ? errorDetails[0].last_error : null
        
        setStats({
          accountsConnected: {
            session: sessionAccounts,
            official: officialAccounts,
            total: accounts.length
          },
          postsToday: 12, // TODO: Implement actual posts today count
          pendingDue: autopilotData.due_accounts || 0,
          lastError: lastError
        })
      } else {
        // Fallback to mock data
        setStats({
          accountsConnected: {
            session: 2,
            official: 1,
            total: 3
          },
          postsToday: 12,
          pendingDue: 3,
          lastError: null
        })
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
      // Fallback to mock data
      setStats({
        accountsConnected: {
          session: 2,
          official: 1,
          total: 3
        },
        postsToday: 12,
        pendingDue: 3,
        lastError: null
      })
    } finally {
      setLoading(false)
    }
  }

  const runAutopilotTick = async () => {
    setRunningTick(true)
    try {
      const response = await fetch(`${API_BASE}/autopilot/tick`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('Autopilot tick result:', data)
        // Refresh stats after tick
        await fetchStats()
      }
    } catch (error) {
      console.error('Error running autopilot tick:', error)
    } finally {
      setRunningTick(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-shimmer w-32 h-32 rounded-full border-4 border-glass-border border-t-primary animate-spin"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="heading-1 gradient-text">Dashboard</h1>
          <p className="text-body mt-2">Overview of your Threads automation</p>
        </div>
        
        <GlassButton
          onClick={runAutopilotTick}
          disabled={runningTick}
          loading={runningTick}
          className="responsive"
        >
          <PlayIcon className="w-5 h-5" />
          {runningTick ? 'Running Tick...' : 'Run Autopilot Tick'}
        </GlassButton>
      </div>

      {/* Stats Cards */}
      <div className="responsive-grid">
        {/* Accounts Connected */}
        <GlassCard className="animate-slide-up" dense>
          <div className="flex items-center gap-4">
            <div className="empty-state-blob">
              <UserGroupIcon className="w-6 h-6 text-primary" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-caption">Accounts Connected</p>
              <div className="flex items-center gap-3 mt-1">
                <p className="heading-3 text-white">{stats?.accountsConnected?.total || 0}</p>
                <div className="flex gap-1">
                  {(stats?.accountsConnected?.session || 0) > 0 && (
                    <StatusChip status="success" className="text-xs">
                      {stats?.accountsConnected?.session} Session
                    </StatusChip>
                  )}
                  {(stats?.accountsConnected?.official || 0) > 0 && (
                    <StatusChip status="info" className="text-xs">
                      {stats?.accountsConnected?.official} Official
                    </StatusChip>
                  )}
                </div>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Posts Today */}
        <GlassCard className="animate-slide-up" dense style={{ animationDelay: '100ms' }}>
          <div className="flex items-center gap-4">
            <div className="empty-state-blob">
              <TrophyIcon className="w-6 h-6 text-accent" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-caption">Posts Today</p>
              <p className="heading-3 text-white mt-1">{stats?.postsToday}</p>
            </div>
          </div>
        </GlassCard>

        {/* Pending Due */}
        <GlassCard className="animate-slide-up" dense style={{ animationDelay: '200ms' }}>
          <div className="flex items-center gap-4">
            <div className="empty-state-blob">
              <ClockIcon className="w-6 h-6 text-amber-400" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-caption">Pending Due (60 min)</p>
              <p className="heading-3 text-white mt-1">{stats?.pendingDue}</p>
            </div>
          </div>
        </GlassCard>

        {/* Last Error */}
        <GlassCard className="animate-slide-up" dense style={{ animationDelay: '300ms' }}>
          <div className="flex items-center gap-4">
            <div className="empty-state-blob">
              <ExclamationTriangleIcon className="w-6 h-6 text-red-400" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-caption">Last Error</p>
              <p className="heading-3 text-white mt-1">
                {stats?.lastError ? '1' : '0'}
              </p>
              {stats?.lastError && (
                <p className="text-xs text-red-400 mt-1 truncate">
                  {stats.lastError}
                </p>
              )}
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Content Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <GlassCard title="Recent Activity" className="animate-slide-up" style={{ animationDelay: '400ms' }}>
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-emerald-400 rounded-full flex-shrink-0"></div>
              <div className="min-w-0 flex-1">
                <p className="text-body text-sm">Posted to @username1</p>
                <p className="text-caption">2 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-blue-400 rounded-full flex-shrink-0"></div>
              <div className="min-w-0 flex-1">
                <p className="text-body text-sm">Scheduled next post</p>
                <p className="text-caption">5 minutes ago</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-2 h-2 bg-emerald-400 rounded-full flex-shrink-0"></div>
              <div className="min-w-0 flex-1">
                <p className="text-body text-sm">Posted to @username2</p>
                <p className="text-caption">15 minutes ago</p>
              </div>
            </div>
          </div>
        </GlassCard>

        <GlassCard title="Autopilot Status" className="animate-slide-up" style={{ animationDelay: '500ms' }}>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-caption">Status</span>
              <StatusChip status="success">Active</StatusChip>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-caption">Mode</span>
              <span className="text-body text-sm">Session-first</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-caption">Next Tick</span>
              <span className="text-body text-sm">2 minutes</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-caption">Max per Tick</span>
              <span className="text-body text-sm">5 accounts</span>
            </div>
          </div>
        </GlassCard>

        <GlassCard title="Content Stats" className="animate-slide-up" style={{ animationDelay: '600ms' }}>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ChatBubbleLeftRightIcon className="w-4 h-4 text-white/60" />
                <span className="text-caption">Captions</span>
              </div>
              <span className="text-body text-sm">45 total</span>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <PhotoIcon className="w-4 h-4 text-white/60" />
                <span className="text-caption">Images</span>
              </div>
              <span className="text-body text-sm">28 total</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-caption">Unused Captions</span>
              <StatusChip status="info">23</StatusChip>
            </div>
          </div>
        </GlassCard>
      </div>
    </div>
  )
}





 