'use client'

import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface EngagementData {
  date: string
  total_engagement: number
  likes: number
  replies: number
  reposts: number
  quotes: number
  post_count: number
  account_count: number
}

interface EngagementStats {
  success: boolean
  data: EngagementData[]
  total_days: number
  error?: string
}

export default function EngagementChart() {
  const [engagementData, setEngagementData] = useState<EngagementData[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState<string>('')
  const [days, setDays] = useState(7)

  const fetchEngagementData = async () => {
    setIsLoading(true)
    setError('')
    
    try {
      const response = await fetch(`/api/stats/engagement?days=${days}`)
      const data: EngagementStats = await response.json()
      
      if (data.success) {
        setEngagementData(data.data)
      } else {
        setError(data.error || 'Failed to fetch engagement data')
      }
    } catch (err) {
      setError('Error fetching engagement data')
      console.error('Error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const refreshEngagementData = async () => {
    setIsRefreshing(true)
    setError('')
    
    try {
      const response = await fetch('/api/stats/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      const result: { success: boolean; error?: string } = await response.json()
      
      if (result.success) {
        // Fetch updated data
        await fetchEngagementData()
      } else {
        setError(result.error || 'Failed to refresh engagement data')
      }
    } catch (err) {
      setError('Error refreshing engagement data')
      console.error('Error:', err)
    } finally {
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    fetchEngagementData()
  }, [days])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    })
  }

  const totalEngagement = engagementData.reduce((sum, item) => sum + item.total_engagement, 0)
  const totalPosts = engagementData.reduce((sum, item) => sum + item.post_count, 0)
  const avgEngagement = totalPosts > 0 ? Math.round(totalEngagement / totalPosts) : 0

  return (
    <div className="space-y-8">
      {/* Header with controls */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Engagement Analytics</h2>
          <p className="text-gray-300">Daily engagement across all Threads accounts</p>
        </div>
        <div className="flex gap-3">
          <select 
            value={days} 
            onChange={(e) => setDays(Number(e.target.value))}
            className="modern-button px-4 py-2 bg-transparent border border-gray-600 text-white"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
          <button 
            onClick={refreshEngagementData}
            disabled={isRefreshing}
            className="modern-button px-6 py-2 glow-on-hover"
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{totalEngagement.toLocaleString()}</div>
          <div className="text-sm text-gray-300">Total Engagement</div>
        </div>
        
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{totalPosts}</div>
          <div className="text-sm text-gray-300">Total Posts</div>
        </div>
        
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{avgEngagement}</div>
          <div className="text-sm text-gray-300">Avg Engagement</div>
        </div>
        
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{engagementData.length}</div>
          <div className="text-sm text-gray-300">Days Tracked</div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="modern-card p-4 border border-red-500/30">
          <div className="text-red-400">{error}</div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <div className="text-gray-300">Loading engagement data...</div>
        </div>
      )}

      {/* Charts */}
      {!isLoading && engagementData.length > 0 && (
        <div className="space-y-8">
          {/* Total Engagement Line Chart */}
          <div className="modern-card p-6">
            <h3 className="text-xl font-bold text-white mb-6">Daily Total Engagement</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={engagementData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  tick={{ fontSize: 12, fill: '#9ca3af' }}
                  stroke="rgba(255,255,255,0.3)"
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#9ca3af' }}
                  stroke="rgba(255,255,255,0.3)"
                />
                <Tooltip 
                  labelFormatter={formatDate}
                  formatter={(value: number) => [value.toLocaleString(), 'Engagement']}
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="total_engagement" 
                  stroke="#B693FE" 
                  strokeWidth={3}
                  name="Total Engagement"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Engagement Breakdown Bar Chart */}
          <div className="modern-card p-6">
            <h3 className="text-xl font-bold text-white mb-6">Engagement Breakdown</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={engagementData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  tick={{ fontSize: 12, fill: '#9ca3af' }}
                  stroke="rgba(255,255,255,0.3)"
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#9ca3af' }}
                  stroke="rgba(255,255,255,0.3)"
                />
                <Tooltip 
                  labelFormatter={formatDate}
                  formatter={(value: number) => [value.toLocaleString(), 'Count']}
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Bar dataKey="likes" fill="#ef4444" name="Likes" />
                <Bar dataKey="replies" fill="#f59e0b" name="Replies" />
                <Bar dataKey="reposts" fill="#10b981" name="Reposts" />
                <Bar dataKey="quotes" fill="#8b5cf6" name="Quotes" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Posts Per Day Chart */}
          <div className="modern-card p-6">
            <h3 className="text-xl font-bold text-white mb-6">Posts Per Day</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={engagementData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis 
                  dataKey="date" 
                  tickFormatter={formatDate}
                  tick={{ fontSize: 12, fill: '#9ca3af' }}
                  stroke="rgba(255,255,255,0.3)"
                />
                <YAxis 
                  tick={{ fontSize: 12, fill: '#9ca3af' }}
                  stroke="rgba(255,255,255,0.3)"
                />
                <Tooltip 
                  labelFormatter={formatDate}
                  formatter={(value: number) => [value, 'Posts']}
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.9)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="post_count" 
                  stroke="#06b6d4" 
                  strokeWidth={3}
                  name="Posts"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && engagementData.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="text-gray-300 text-lg mb-2">No engagement data available</div>
          <p className="text-gray-400">Add some accounts and refresh the data to see engagement analytics</p>
        </div>
      )}
    </div>
  )
} 