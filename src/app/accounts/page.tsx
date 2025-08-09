'use client'

import { useEffect, useState, useRef } from 'react'
import { 
  UserPlusIcon, 
  PlayIcon,
  CogIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  EllipsisVerticalIcon,
  LinkIcon
} from '@heroicons/react/24/outline'
import { 
  fetchAccounts, 
  patchAccount, 
  startOAuth, 
  testPost,
  updateAutopilot,
  updateCadence 
} from '@/lib/api/client'
import type { Account } from '@/types/accounts'
import GlassCard from '@/components/ui/GlassCard'
import GlassButton from '@/components/ui/GlassButton'
import StatusChip from '@/components/ui/StatusChip'
import GlassModal from '@/components/ui/GlassModal'
import { API_BASE } from '@/lib/config'

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
  const [testingPosts, setTestingPosts] = useState<{[key: string]: boolean}>({})

  useEffect(() => {
    loadAccounts()
    
    // Check for OAuth status/message in URL params
    const urlParams = new URLSearchParams(window.location.search)
    const status = urlParams.get('status')
    const message = urlParams.get('message')
    
    if (status === 'success') {
      setMessage(message || 'Account connected successfully!')
      // Clear URL params
      window.history.replaceState({}, '', '/accounts')
    } else if (status === 'error') {
      setError(message || 'OAuth connection failed')
      // Clear URL params
      window.history.replaceState({}, '', '/accounts')
    }
  }, [])

  const loadAccounts = async () => {
    try {
      setLoading(true)
      const accountsData = await fetchAccounts()
      setAccounts(accountsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch accounts')
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
        await loadAccounts()
      } else {
        setError(data.error || 'Failed to create account')
      }
    } catch (err) {
      setError('Failed to create account')
    }
  }

  const toggleAutopilot = async (accountId: string, enabled: boolean) => {
    // Optimistic update
    setAccounts(prev => prev.map(acc => 
      acc.id === accountId 
        ? { ...acc, autopilot_enabled: enabled }
        : acc
    ))
    
    try {
      const result = await updateAutopilot(accountId, enabled)
      
      // Update with server response (includes next_run_at)
      setAccounts(prev => prev.map(acc => 
        acc.id === accountId 
          ? { 
              ...acc, 
              autopilot_enabled: result.autopilot_enabled,
              next_run_at: result.next_run_at 
            }
          : acc
      ))
      
      setMessage(`Autopilot ${enabled ? 'enabled' : 'disabled'} successfully`)
    } catch (err) {
      // Revert optimistic update on error
      setAccounts(prev => prev.map(acc => 
        acc.id === accountId 
          ? { ...acc, autopilot_enabled: !enabled }
          : acc
      ))
      setError(err instanceof Error ? err.message : 'Failed to update autopilot setting')
    }
  }

  const handleCadenceChange = async (accountId: string, minutes: number) => {
    // Optimistic update
    setAccounts(prev => prev.map(acc => 
      acc.id === accountId 
        ? { ...acc, cadence_minutes: minutes }
        : acc
    ))
    
    try {
      const result = await updateCadence(accountId, minutes)
      
      // Update with server response (includes next_run_at if autopilot enabled)
      setAccounts(prev => prev.map(acc => 
        acc.id === accountId 
          ? { 
              ...acc, 
              cadence_minutes: result.cadence_minutes,
              next_run_at: result.next_run_at 
            }
          : acc
      ))
      
      setMessage('Cadence updated successfully')
    } catch (err) {
      // Revert optimistic update on error
      await loadAccounts()
      setError(err instanceof Error ? err.message : 'Failed to update cadence')
    }
  }



  const handleTestPost = async (accountId: string) => {
    try {
      setTestingPosts(prev => ({ ...prev, [accountId]: true }))
      const result = await testPost(accountId)
      
      if (result.ok) {
        setMessage(`Test post successful! Method: ${result.post?.method}`)
        await loadAccounts()
      } else {
        if (result.error?.includes('Rate limit')) {
          setError(`Rate limit: ${result.error}`)
        } else if (result.error?.includes('Cannot post') || result.error?.includes('not connected')) {
          setError(`Cannot post: ${result.error}`)
        } else {
          setError(result.error || 'Test post failed')
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send test post')
    } finally {
      setTestingPosts(prev => ({ ...prev, [accountId]: false }))
    }
  }

  const handleConnect = (accountId: string) => {
    startOAuth(accountId)
  }

  const resetForm = () => {
    setFormData({ username: '', description: '' })
    setError('')
    setMessage('')
  }

  const getConnectionBadge = (account: Account) => {
    if (account.threads_connected) {
      switch (account.connection_status) {
        case 'connected_session':
          return <StatusChip status="success">Connected (Session)</StatusChip>
        case 'connected_official':
          return <StatusChip status="info">Connected (Official)</StatusChip>
        default:
          return <StatusChip status="success">Connected</StatusChip>
      }
    } else {
      return <StatusChip status="error">Disconnected</StatusChip>
    }
  }

  const formatDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'Never'
    try {
      return new Date(dateString).toLocaleString()
    } catch {
      return 'Never'
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
                      {account.oauth_status && account.oauth_status.startsWith('error:') && (
                        <div className="mt-1 px-2 py-1 bg-red-500/20 border border-red-400/30 rounded text-xs text-red-300">
                          {account.oauth_status.replace('error: ', '')}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    {getConnectionBadge(account)}
                  </div>
                  
                  <div>
                    <label className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={account.autopilot_enabled}
                        disabled={!account.threads_connected}
                        onChange={(e) => toggleAutopilot(account.id, e.target.checked)}
                        className="rounded border-glass-border bg-glass-100 text-primary focus:ring-primary/60 disabled:opacity-50 disabled:cursor-not-allowed"
                        title={!account.threads_connected ? "Reconnect account first" : ""}
                      />
                      <span className="text-sm text-white/80">
                        {account.autopilot_enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </label>
                  </div>
                  
                  <div>
                    <select
                      value={account.cadence_minutes}
                      disabled={!account.autopilot_enabled}
                      onChange={(e) => handleCadenceChange(account.id, parseInt(e.target.value))}
                      className="glass-input w-20 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                      title={!account.autopilot_enabled ? "Enable autopilot first" : ""}
                    >
                      <option value={5}>5m</option>
                      <option value={10}>10m</option>
                      <option value={15}>15m</option>
                      <option value={30}>30m</option>
                      <option value={60}>1h</option>
                      <option value={120}>2h</option>
                      <option value={180}>3h</option>
                      <option value={240}>4h</option>
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
                      {/* Reconnect Button */}
                      {!account.threads_connected && (
                        <GlassButton
                          size="sm"
                          onClick={() => handleConnect(account.id)}
                          className="relative"
                        >
                          <LinkIcon className="w-4 h-4" />
                          Reconnect
                          {/* Connection indicator dot */}
                          <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-400 rounded-full animate-pulse" 
                                title="Reconnect via Meta OAuth" />
                        </GlassButton>
                      )}
                      
                      {/* Test Post */}
                      <GlassButton
                        variant="ghost"
                        size="sm"
                        onClick={() => handleTestPost(account.id)}
                        loading={testingPosts[account.id]}
                        disabled={testingPosts[account.id]}
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
                      <div className="flex-1">
                        <p className="font-medium text-white">@{account.username}</p>
                        {account.description && (
                          <p className="text-caption">{account.description}</p>
                        )}
                        {account.oauth_status && account.oauth_status.startsWith('error:') && (
                          <div className="mt-2 px-2 py-1 bg-red-500/20 border border-red-400/30 rounded text-xs text-red-300">
                            {account.oauth_status.replace('error: ', '')}
                          </div>
                        )}
                      </div>
                      {getConnectionBadge(account)}
                    </div>
                    
                    {/* Settings */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-caption mb-2">Autopilot</p>
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={account.autopilot_enabled}
                            disabled={!account.threads_connected}
                            onChange={(e) => toggleAutopilot(account.id, e.target.checked)}
                            className="rounded border-glass-border bg-glass-100 text-primary focus:ring-primary/60 disabled:opacity-50 disabled:cursor-not-allowed"
                            title={!account.threads_connected ? "Reconnect account first" : ""}
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
                          disabled={!account.autopilot_enabled}
                          onChange={(e) => handleCadenceChange(account.id, parseInt(e.target.value))}
                          className="glass-input w-full text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                          title={!account.autopilot_enabled ? "Enable autopilot first" : ""}
                        >
                          <option value={5}>5 minutes</option>
                          <option value={10}>10 minutes</option>
                          <option value={15}>15 minutes</option>
                          <option value={30}>30 minutes</option>
                          <option value={60}>1 hour</option>
                          <option value={120}>2 hours</option>
                          <option value={180}>3 hours</option>
                          <option value={240}>4 hours</option>
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
                      {!account.threads_connected && (
                        <GlassButton
                          onClick={() => handleConnect(account.id)}
                          className="flex-1 relative"
                        >
                          <LinkIcon className="w-4 h-4" />
                          Reconnect
                          {/* Connection indicator dot */}
                          <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-400 rounded-full animate-pulse" 
                                title="Reconnect via Meta OAuth" />
                        </GlassButton>
                      )}
                      
                      <GlassButton
                        variant="ghost"
                        onClick={() => handleTestPost(account.id)}
                        loading={testingPosts[account.id]}
                        disabled={testingPosts[account.id]}
                        className={!account.threads_connected ? 'flex-1' : 'w-full'}
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