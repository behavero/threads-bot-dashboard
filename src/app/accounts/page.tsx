'use client'

import { useEffect, useState, useRef } from 'react'
import { 
  UserPlusIcon, 
  CloudArrowUpIcon,
  PlayIcon,
  CogIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  EllipsisVerticalIcon
} from '@heroicons/react/24/outline'
import { API_BASE } from '@/lib/config'
import GlassCard from '@/components/ui/GlassCard'
import GlassButton from '@/components/ui/GlassButton'
import StatusChip from '@/components/ui/StatusChip'
import GlassModal from '@/components/ui/GlassModal'

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
        return <StatusChip status="success">Connected (Session)</StatusChip>
      case 'connected_official':
        return <StatusChip status="info">Connected (Official)</StatusChip>
      default:
        return <StatusChip status="error">Disconnected</StatusChip>
    }
  }

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never'
    return new Date(dateString).toLocaleString()
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
          <h1 className="heading-1 gradient-text">Accounts</h1>
          <p className="text-body mt-2">Manage your Threads accounts and autopilot settings</p>
        </div>
        
        <GlassButton
          onClick={() => setShowModal(true)}
          className="responsive"
        >
          <UserPlusIcon className="w-5 h-5" />
          Add Account
        </GlassButton>
      </div>

      {/* Messages */}
      {error && (
        <GlassCard className="border-red-500/20 bg-red-500/10 animate-slide-down">
          <div className="flex items-center gap-3">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-400 flex-shrink-0" />
            <p className="text-red-300 flex-1">{error}</p>
            <GlassButton variant="ghost" size="sm" onClick={() => setError('')} className="!p-1">
              <XMarkIcon className="w-4 h-4" />
            </GlassButton>
          </div>
        </GlassCard>
      )}

      {message && (
        <GlassCard className="border-emerald-500/20 bg-emerald-500/10 animate-slide-down">
          <div className="flex items-center gap-3">
            <CheckIcon className="w-5 h-5 text-emerald-400 flex-shrink-0" />
            <p className="text-emerald-300 flex-1">{message}</p>
            <GlassButton variant="ghost" size="sm" onClick={() => setMessage('')} className="!p-1">
              <XMarkIcon className="w-4 h-4" />
            </GlassButton>
          </div>
        </GlassCard>
      )}

      {/* Accounts Section */}
      <GlassCard 
        title="Connected Accounts" 
        subtitle={`${accounts.length} total accounts`}
        className="animate-slide-up"
      >
        {accounts.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-blob">
              <UserPlusIcon className="w-8 h-8 text-primary" />
            </div>
            <h3 className="heading-4 text-white mb-2">No accounts yet</h3>
            <p className="text-body mb-6">Get started by adding your first Threads account</p>
            <GlassButton onClick={() => setShowModal(true)}>
              Add Your First Account
            </GlassButton>
          </div>
        ) : (
          <>
            {/* Desktop Table */}
            <div className="hidden lg:block glass-table">
              <div className="grid grid-cols-7 glass-table-header">
                <div>Username</div>
                <div>Status</div>
                <div>Autopilot</div>
                <div>Cadence</div>
                <div>Next Run</div>
                <div>Last Posted</div>
                <div>Actions</div>
              </div>
              
              {accounts.map((account, index) => (
                <div key={account.id} className="grid grid-cols-7 glass-table-row" style={{ animationDelay: `${index * 100}ms` }}>
                  <div>
                    <div>
                      <p className="font-medium text-white">@{account.username}</p>
                      {account.description && (
                        <p className="text-caption">{account.description}</p>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    {getConnectionBadge(account.connection_status)}
                  </div>
                  
                  <div>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={account.autopilot_enabled}
                        onChange={(e) => toggleAutopilot(account.id, e.target.checked)}
                        className="rounded border-glass-border bg-glass-100 text-primary focus:ring-primary/60"
                      />
                      <span className="text-sm text-white/80">
                        {account.autopilot_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </label>
                  </div>
                  
                  <div>
                    <select
                      value={account.cadence_minutes}
                      onChange={(e) => updateCadence(account.id, parseInt(e.target.value))}
                      className="glass-input w-20 text-sm"
                    >
                      <option value={5}>5m</option>
                      <option value={10}>10m</option>
                      <option value={15}>15m</option>
                      <option value={30}>30m</option>
                      <option value={60}>1h</option>
                    </select>
                  </div>
                  
                  <div>
                    <span className="text-caption">
                      {formatDate(account.next_run_at)}
                    </span>
                  </div>
                  
                  <div>
                    <span className="text-caption">
                      {formatDate(account.last_posted_at)}
                    </span>
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2">
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
                          <GlassButton
                            variant="ghost"
                            size="sm"
                            onClick={() => sessionInputRefs.current[account.id]?.click()}
                            disabled={sessionUploads[account.id]}
                            loading={sessionUploads[account.id]}
                          >
                            <CloudArrowUpIcon className="w-4 h-4" />
                            Session
                          </GlassButton>
                        </div>
                      )}
                      
                      {/* Test Post */}
                      <GlassButton
                        variant="ghost"
                        size="sm"
                        onClick={() => testPost(account.id)}
                      >
                        <PlayIcon className="w-4 h-4" />
                        Test
                      </GlassButton>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Mobile Cards */}
            <div className="lg:hidden space-y-4">
              {accounts.map((account, index) => (
                <GlassCard key={account.id} dense className="animate-slide-up" style={{ animationDelay: `${index * 100}ms` }}>
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-white">@{account.username}</p>
                        {account.description && (
                          <p className="text-caption">{account.description}</p>
                        )}
                      </div>
                      {getConnectionBadge(account.connection_status)}
                    </div>
                    
                    {/* Settings */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-caption mb-2">Autopilot</p>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={account.autopilot_enabled}
                            onChange={(e) => toggleAutopilot(account.id, e.target.checked)}
                            className="rounded border-glass-border bg-glass-100 text-primary focus:ring-primary/60"
                          />
                          <span className="text-sm text-white/80">
                            {account.autopilot_enabled ? 'Enabled' : 'Disabled'}
                          </span>
                        </label>
                      </div>
                      
                      <div>
                        <p className="text-caption mb-2">Cadence</p>
                        <select
                          value={account.cadence_minutes}
                          onChange={(e) => updateCadence(account.id, parseInt(e.target.value))}
                          className="glass-input w-full text-sm"
                        >
                          <option value={5}>5 minutes</option>
                          <option value={10}>10 minutes</option>
                          <option value={15}>15 minutes</option>
                          <option value={30}>30 minutes</option>
                          <option value={60}>1 hour</option>
                        </select>
                      </div>
                    </div>
                    
                    {/* Timestamps */}
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-caption">Next Run</p>
                        <p className="text-white/80">{formatDate(account.next_run_at)}</p>
                      </div>
                      <div>
                        <p className="text-caption">Last Posted</p>
                        <p className="text-white/80">{formatDate(account.last_posted_at)}</p>
                      </div>
                    </div>
                    
                    {/* Actions */}
                    <div className="flex gap-2">
                      {account.connection_status === 'disconnected' && (
                        <div className="relative flex-1">
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
                          <GlassButton
                            variant="ghost"
                            onClick={() => sessionInputRefs.current[account.id]?.click()}
                            disabled={sessionUploads[account.id]}
                            loading={sessionUploads[account.id]}
                            className="w-full"
                          >
                            <CloudArrowUpIcon className="w-4 h-4" />
                            Connect via Session
                          </GlassButton>
                        </div>
                      )}
                      
                      <GlassButton
                        variant="ghost"
                        onClick={() => testPost(account.id)}
                        className={account.connection_status === 'disconnected' ? 'flex-1' : 'w-full'}
                      >
                        <PlayIcon className="w-4 h-4" />
                        Test Post
                      </GlassButton>
                    </div>
                  </div>
                </GlassCard>
              ))}
            </div>
          </>
        )}
      </GlassCard>

      {/* Create Account Modal */}
      <GlassModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Add Threads Account"
        size="md"
      >
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Username *
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="@username"
              className="glass-input"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Description
            </label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Optional description"
              className="glass-input"
            />
          </div>
          
          <div className="flex gap-3 pt-4">
            <GlassButton
              onClick={createAccount}
              disabled={!formData.username}
              className="flex-1"
            >
              Create Account
            </GlassButton>
            <GlassButton
              variant="ghost"
              onClick={() => setShowModal(false)}
              className="flex-1"
            >
              Cancel
            </GlassButton>
          </div>
        </div>
      </GlassModal>
    </div>
  )
}