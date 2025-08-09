'use client'

import { useEffect, useState, useRef } from 'react'
import Layout from '@/components/Layout'
import { 
  UserPlusIcon, 
  CloudArrowUpIcon,
  PlayIcon,
  CogIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'
import { API_BASE } from '@/lib/config'

interface Account {
  id: number
  username: string
  description: string
  status: string
  connection_status: 'connected_session' | 'connected_official' | 'disconnected'
  autopilot_enabled: boolean
  cadence_minutes: number
  next_run_at: string | null
  last_posted_at: string | null
  created_at: string
}

interface AccountFormData {
  username: string
  description: string
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState<AccountFormData>({
    username: '',
    description: ''
  })
  const [sessionUploads, setSessionUploads] = useState<{[key: number]: boolean}>({})
  const sessionInputRefs = useRef<{[key: number]: HTMLInputElement}>({})

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/api/accounts`)
      const data = await response.json()
      
      if (data.ok) {
        setAccounts(data.accounts || [])
      } else {
        setError(data.error || 'Failed to fetch accounts')
      }
    } catch (err) {
      setError('Failed to connect to server')
    } finally {
      setLoading(false)
    }
  }

  const createAccount = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/accounts/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage('Account created successfully!')
        setShowModal(false)
        resetForm()
        await fetchAccounts()
      } else {
        setError(data.error || 'Failed to create account')
      }
    } catch (err) {
      setError('Failed to create account')
    }
  }

  const toggleAutopilot = async (accountId: number, enabled: boolean) => {
    try {
      const response = await fetch(`${API_BASE}/api/accounts/${accountId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ autopilot_enabled: enabled })
      })
      
      if (response.ok) {
        await fetchAccounts()
        setMessage(`Autopilot ${enabled ? 'enabled' : 'disabled'} successfully`)
      }
    } catch (err) {
      setError('Failed to update autopilot setting')
    }
  }

  const updateCadence = async (accountId: number, cadence: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/accounts/${accountId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cadence_minutes: cadence })
      })
      
      if (response.ok) {
        await fetchAccounts()
        setMessage('Cadence updated successfully')
      }
    } catch (err) {
      setError('Failed to update cadence')
    }
  }

  const uploadSession = async (accountId: number, file: File) => {
    try {
      setSessionUploads(prev => ({ ...prev, [accountId]: true }))
      
      const formData = new FormData()
      formData.append('session_file', file)
      
      const response = await fetch(`${API_BASE}/api/accounts/${accountId}/session`, {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage('Session uploaded successfully!')
        await fetchAccounts()
      } else {
        setError(data.error || 'Failed to upload session')
      }
    } catch (err) {
      setError('Failed to upload session')
    } finally {
      setSessionUploads(prev => ({ ...prev, [accountId]: false }))
    }
  }

  const testPost = async (accountId: number) => {
    try {
      const response = await fetch(`${API_BASE}/api/threads/post`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_id: accountId,
          text: `Test post from Threads Bot! 🚀 ${new Date().toLocaleTimeString()}`,
          is_test: true
        })
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage(`Test post successful! Method: ${data.post?.method}`)
        await fetchAccounts()
      } else {
        if (response.status === 429) {
          setError(`Rate limit: ${data.error}`)
        } else if (response.status === 403) {
          setError(`Cannot post: ${data.error}`)
        } else {
          setError(data.error || 'Test post failed')
        }
      }
    } catch (err) {
      setError('Failed to send test post')
    }
  }

  const resetForm = () => {
    setFormData({ username: '', description: '' })
    setError('')
    setMessage('')
  }

  const getConnectionBadge = (status: string) => {
    switch (status) {
      case 'connected_session':
        return <span className="badge-success">Connected (Session)</span>
      case 'connected_official':
        return <span className="badge-info">Connected (Official)</span>
      default:
        return <span className="badge-error">Disconnected</span>
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleString()
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
            <h1 className="text-3xl font-bold text-gray-900">Accounts</h1>
            <p className="text-gray-600 mt-1">Manage your Threads accounts and autopilot settings</p>
          </div>
          
          <button
            onClick={() => setShowModal(true)}
            className="btn-primary flex items-center space-x-2"
          >
            <UserPlusIcon className="w-5 h-5" />
            <span>Add Account</span>
          </button>
        </div>

        {/* Messages */}
        {error && (
          <div className="glass-card border-red-200 bg-red-50 rounded-xl p-4">
            <div className="flex items-center">
              <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mr-2" />
              <p className="text-red-700">{error}</p>
              <button onClick={() => setError('')} className="ml-auto">
                <XMarkIcon className="w-5 h-5 text-red-600" />
              </button>
            </div>
          </div>
        )}

        {message && (
          <div className="glass-card border-green-200 bg-green-50 rounded-xl p-4">
            <div className="flex items-center">
              <CheckIcon className="w-5 h-5 text-green-600 mr-2" />
              <p className="text-green-700">{message}</p>
              <button onClick={() => setMessage('')} className="ml-auto">
                <XMarkIcon className="w-5 h-5 text-green-600" />
              </button>
            </div>
          </div>
        )}

        {/* Accounts Table */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Connected Accounts</h2>
            <span className="text-sm text-gray-500">{accounts.length} total</span>
          </div>

          {accounts.length === 0 ? (
            <div className="text-center py-12">
              <UserPlusIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No accounts yet</h3>
              <p className="text-gray-600 mb-4">Get started by adding your first Threads account</p>
              <button onClick={() => setShowModal(true)} className="btn-primary">
                Add Your First Account
              </button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Username</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Autopilot</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Cadence</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Next Run</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Last Posted</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {accounts.map((account) => (
                    <tr key={account.id} className="border-b border-gray-100 hover:bg-gray-50/50">
                      <td className="py-4 px-4">
                        <div>
                          <p className="font-medium text-gray-900">@{account.username}</p>
                          {account.description && (
                            <p className="text-sm text-gray-500">{account.description}</p>
                          )}
                        </div>
                      </td>
                      
                      <td className="py-4 px-4">
                        {getConnectionBadge(account.connection_status)}
                      </td>
                      
                      <td className="py-4 px-4">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={account.autopilot_enabled}
                            onChange={(e) => toggleAutopilot(account.id, e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="ml-2 text-sm text-gray-900">
                            {account.autopilot_enabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </label>
                      </td>
                      
                      <td className="py-4 px-4">
                        <select
                          value={account.cadence_minutes}
                          onChange={(e) => updateCadence(account.id, parseInt(e.target.value))}
                          className="form-select w-20 text-sm"
                        >
                          <option value={5}>5m</option>
                          <option value={10}>10m</option>
                          <option value={15}>15m</option>
                          <option value={30}>30m</option>
                          <option value={60}>1h</option>
                        </select>
                      </td>
                      
                      <td className="py-4 px-4">
                        <span className="text-sm text-gray-600">
                          {formatDate(account.next_run_at)}
                        </span>
                      </td>
                      
                      <td className="py-4 px-4">
                        <span className="text-sm text-gray-600">
                          {formatDate(account.last_posted_at)}
                        </span>
                      </td>
                      
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          {/* Session Upload */}
                          {account.connection_status === 'disconnected' && (
                            <div className="relative">
                              <input
                                ref={(el) => {
                                  if (el) sessionInputRefs.current[account.id] = el
                                }}
                                type="file"
                                accept=".json"
                                onChange={(e) => {
                                  const file = e.target.files?.[0]
                                  if (file) uploadSession(account.id, file)
                                }}
                                className="hidden"
                              />
                              <button
                                onClick={() => sessionInputRefs.current[account.id]?.click()}
                                disabled={sessionUploads[account.id]}
                                className="btn-secondary text-xs flex items-center space-x-1"
                              >
                                <CloudArrowUpIcon className="w-4 h-4" />
                                <span>{sessionUploads[account.id] ? 'Uploading...' : 'Session'}</span>
                              </button>
                            </div>
                          )}
                          
                          {/* Test Post */}
                          <button
                            onClick={() => testPost(account.id)}
                            className="btn-secondary text-xs flex items-center space-x-1"
                          >
                            <PlayIcon className="w-4 h-4" />
                            <span>Test</span>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Create Account Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="card w-full max-w-md">
              <div className="card-header">
                <h3 className="card-title">Add Threads Account</h3>
                <button onClick={() => setShowModal(false)}>
                  <XMarkIcon className="w-6 h-6 text-gray-400" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username *
                  </label>
                  <input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    placeholder="@username"
                    className="form-input"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <input
                    type="text"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Optional description"
                    className="form-input"
                  />
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={createAccount}
                    className="btn-primary flex-1"
                    disabled={!formData.username}
                  >
                    Create Account
                  </button>
                  <button
                    onClick={() => setShowModal(false)}
                    className="btn-ghost flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}