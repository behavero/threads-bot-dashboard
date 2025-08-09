'use client'

import { useEffect, useState } from 'react'
import Layout from '@/components/Layout'
import { 
  UserGroupIcon, 
  ChatBubbleLeftRightIcon, 
  PhotoIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  PlayIcon
} from '@heroicons/react/24/outline'

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
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/accounts`),
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/autopilot/status`)
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
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/autopilot/tick`, {
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
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Overview of your Threads automation</p>
          </div>
          
          <button
            onClick={runAutopilotTick}
            disabled={runningTick}
            className="btn-primary flex items-center space-x-2"
          >
            <PlayIcon className="w-5 h-5" />
            <span>{runningTick ? 'Running...' : 'Run Autopilot Tick'}</span>
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Accounts Connected */}
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-blue-100">
                <UserGroupIcon className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Accounts Connected</p>
                <div className="flex items-center space-x-2">
                  <p className="text-2xl font-bold text-gray-900">{stats?.accountsConnected?.total || 0}</p>
                  <div className="flex space-x-1">
                    {(stats?.accountsConnected?.session || 0) > 0 && (
                      <span className="badge-success text-xs">
                        {stats?.accountsConnected?.session} Session
                      </span>
                    )}
                    {(stats?.accountsConnected?.official || 0) > 0 && (
                      <span className="badge-info text-xs">
                        {stats?.accountsConnected?.official} Official
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Posts Today */}
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-green-100">
                <ChatBubbleLeftRightIcon className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Posts Today</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.postsToday}</p>
              </div>
            </div>
          </div>

          {/* Pending Due */}
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-amber-100">
                <ClockIcon className="w-6 h-6 text-amber-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Pending Due (60 min)</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.pendingDue}</p>
              </div>
            </div>
          </div>

          {/* Last Error */}
          <div className="card">
            <div className="flex items-center">
              <div className="p-3 rounded-xl bg-red-100">
                <ExclamationTriangleIcon className="w-6 h-6 text-red-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Last Error</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stats?.lastError ? '1' : '0'}
                </p>
                {stats?.lastError && (
                  <p className="text-xs text-red-600 mt-1 truncate">
                    {stats.lastError}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card">
            <h3 className="card-title">Recent Activity</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Posted to @username1</p>
                  <p className="text-xs text-gray-500">2 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Scheduled next post</p>
                  <p className="text-xs text-gray-500">5 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">Posted to @username2</p>
                  <p className="text-xs text-gray-500">15 minutes ago</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="card-title">Autopilot Status</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Status</span>
                <span className="badge-success">Active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Mode</span>
                <span className="text-sm text-gray-900">Session-first</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Next Tick</span>
                <span className="text-sm text-gray-900">2 minutes</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Max per Tick</span>
                <span className="text-sm text-gray-900">5 accounts</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="card-title">Content Stats</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ChatBubbleLeftRightIcon className="w-5 h-5 text-gray-400" />
                  <span className="text-sm text-gray-600">Captions</span>
                </div>
                <span className="text-sm text-gray-900">45 total</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <PhotoIcon className="w-5 h-5 text-gray-400" />
                  <span className="text-sm text-gray-600">Images</span>
                </div>
                <span className="text-sm text-gray-900">28 total</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Unused Captions</span>
                <span className="badge-info">23</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}





 