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
      
      const result = await response.json()
      
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
    <div className="space-y-6">
      {/* Header with controls */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">Engagement Analytics</h2>
          <p className="text-gray-600">Daily engagement across all Threads accounts</p>
        </div>
        <div className="flex gap-2">
          <select 
            value={days} 
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-3 py-2 border rounded-md"
          >
            <option value={7}>Last 7 days</option>
            <option value={14}>Last 14 days</option>
            <option value={30}>Last 30 days</option>
          </select>
          <Button 
            onClick={refreshEngagementData}
            disabled={isRefreshing}
            variant="outline"
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Engagement</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalEngagement.toLocaleString()}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Posts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalPosts}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Engagement</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgEngagement}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Days Tracked</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{engagementData.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-8">
          <div className="text-gray-600">Loading engagement data...</div>
        </div>
      )}

      {/* Charts */}
      {!isLoading && engagementData.length > 0 && (
        <div className="space-y-6">
          {/* Total Engagement Line Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Daily Total Engagement</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={engagementData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={formatDate}
                    formatter={(value: number) => [value.toLocaleString(), 'Engagement']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="total_engagement" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    name="Total Engagement"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Engagement Breakdown Bar Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Engagement Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={engagementData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={formatDate}
                    formatter={(value: number) => [value.toLocaleString(), 'Count']}
                  />
                  <Legend />
                  <Bar dataKey="likes" fill="#ef4444" name="Likes" />
                  <Bar dataKey="replies" fill="#f59e0b" name="Replies" />
                  <Bar dataKey="reposts" fill="#10b981" name="Reposts" />
                  <Bar dataKey="quotes" fill="#8b5cf6" name="Quotes" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Posts Per Day Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Posts Per Day</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={engagementData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={formatDate}
                    formatter={(value: number) => [value, 'Posts']}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="post_count" 
                    stroke="#06b6d4" 
                    strokeWidth={2}
                    name="Posts"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && engagementData.length === 0 && !error && (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg">No engagement data available</div>
          <p className="text-gray-400 mt-2">Add some accounts and refresh the data to see engagement analytics</p>
        </div>
      )}
    </div>
  )
} 