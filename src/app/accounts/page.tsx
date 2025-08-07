'use client'

import { useState, useEffect } from 'react'

interface Account {
  id: number
  username: string
  email: string
  password: string
  description: string
  posting_config: any
  fingerprint_config: any
  status: 'enabled' | 'disabled'
  is_active: boolean
  created_at: string
  last_posted?: string
}

interface AccountFormData {
  username: string
  password: string
  description: string
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const [hidePassword, setHidePassword] = useState(false)
  const [formData, setFormData] = useState<AccountFormData>({
    username: '',
    password: '',
    description: ''
  })

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      console.log('Fetching accounts...')
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/accounts')
      const data = await response.json()
      
      console.log('Accounts response:', data)
      
      // Handle both old format ({"accounts": [...]}) and new format ({"success": true, "accounts": [...]})
      if (data.success === true || (data.accounts && Array.isArray(data.accounts))) {
        setAccounts(data.accounts || [])
        setError('') // Clear any previous errors
        console.log('Accounts loaded:', (data.accounts || []).length)
      } else {
        console.error('Failed to fetch accounts:', data.error)
        setError(data.error || 'Failed to fetch accounts')
        setAccounts([])
      }
    } catch (err) {
      console.error('Error fetching accounts:', err)
      setError('Error fetching accounts')
      setAccounts([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')

    try {
      if (editingAccount) {
        // Handle editing existing account
        const url = `https://threads-bot-dashboard-3.onrender.com/api/accounts/${editingAccount.id}`
        
        const response = await fetch(url, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: formData.username,
            password: formData.password,
            description: formData.description
          })
        })

        const data = await response.json()

        if (data.success) {
          setShowModal(false)
          setEditingAccount(null)
          resetForm()
          await fetchAccounts()
          setMessage('Account updated successfully!')
        } else {
          setError(data.error || 'Failed to update account')
        }
      } else {
        // Handle creating new account via login
        console.log('Creating account via login...')
        
        const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/accounts/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: formData.username,
            password: formData.password
          })
        })

        const data = await response.json()
        console.log('Login response:', data)

        if (data.success) {
          setShowModal(false)
          resetForm()
          await fetchAccounts()
          setMessage(`Account created successfully! ${data.user_info?.followers || 0} followers, ${data.user_info?.posts || 0} posts`)
          setHidePassword(true) // Hide password for security
        } else {
          setError(data.error || 'Failed to create account')
        }
      }
    } catch (err) {
      console.error('Error saving account:', err)
      setError('Error saving account')
    }
  }

  const handleEdit = (account: Account) => {
    setEditingAccount(account)
    setFormData({
      username: account.username,
      password: account.password || '',
      description: account.description || ''
    })
    setShowModal(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this account?')) return

    try {
      const response = await fetch(`https://threads-bot-dashboard-3.onrender.com/api/accounts/${id}`, {
        method: 'DELETE'
      })

      const data = await response.json()

      if (data.success) {
        await fetchAccounts()
      } else {
        setError(data.error || 'Failed to delete account')
      }
    } catch (err) {
      setError('Error deleting account')
    }
  }

  const handleToggleStatus = async (account: Account) => {
    try {
      const newStatus = account.status === 'enabled' ? 'disabled' : 'enabled'
      
      const response = await fetch(`https://threads-bot-dashboard-3.onrender.com/api/accounts/${account.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...account,
          status: newStatus
        })
      })

      const data = await response.json()

      if (data.success) {
        await fetchAccounts()
      } else {
        setError(data.error || 'Failed to update account status')
      }
    } catch (err) {
      setError('Error updating account status')
    }
  }

  const resetForm = () => {
    setFormData({
      username: '',
      password: '',
      description: ''
    })
    setHidePassword(false)
  }

  const openAddModal = () => {
    setEditingAccount(null)
    resetForm()
    setShowModal(true)
  }

  const testLogin = async () => {
    try {
      setError('')
      console.log('Testing login...')
      
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/accounts/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: 'test_user',
          password: 'test_pass'
        })
      })
      
      const data = await response.json()
      console.log('Login test response:', data)
      
      if (data.success) {
        setMessage('Login test successful!')
      } else {
        setError(data.error || 'Login test failed')
      }
    } catch (err) {
      console.error('Login test error:', err)
      setError('Login test failed')
    }
  }

  const testSession = async (username: string) => {
    try {
      setError('')
      console.log(`Testing session for ${username}...`)
      
      const response = await fetch(`https://threads-bot-dashboard-3.onrender.com/api/accounts/${username}/test-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          password: 'test_password' // This would need to be provided by user
        })
      })
      
      const data = await response.json()
      console.log('Session test response:', data)
      
      if (data.success) {
        setMessage(`Session test successful for ${username}! ${data.user_info?.followers || 0} followers`)
      } else {
        setError(data.error || 'Session test failed')
      }
    } catch (err) {
      console.error('Session test error:', err)
      setError('Session test failed')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Threads Accounts</h2>
          <p className="text-gray-300">Manage your Threads accounts and posting settings</p>
        </div>
        <div className="flex space-x-4">
          <button
            onClick={testLogin}
            className="modern-button px-4 py-2 text-sm"
          >
            Test Login
          </button>
          <button
            onClick={openAddModal}
            className="modern-button px-6 py-3 glow-on-hover"
          >
            Add Account
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="modern-card p-4 border border-red-500/30">
          <div className="text-red-400">{error}</div>
        </div>
      )}

      {/* Success Message */}
      {message && (
        <div className="modern-card p-4 border border-green-500/30">
          <div className="text-green-400">{message}</div>
        </div>
      )}

      {/* Accounts Grid */}
      {accounts.length === 0 ? (
        <div className="modern-card p-12 text-center">
          <div className="text-6xl mb-4">📱</div>
          <h3 className="text-xl font-semibold text-white mb-2">No Accounts Yet</h3>
          <p className="text-gray-300 mb-6">Add your first Threads account to start automating posts</p>
          <button
            onClick={openAddModal}
            className="modern-button px-6 py-3 glow-on-hover"
          >
            Add Your First Account
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accounts.map((account) => (
            <div key={account.id} className="modern-card p-6 hover:scale-105 transition-transform duration-300">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-white">{account.username}</h3>
                  <p className="text-gray-400 text-sm">{account.email}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleToggleStatus(account)}
                    className={`w-12 h-6 rounded-full transition-colors ${
                      account.status === 'enabled' 
                        ? 'bg-green-500' 
                        : 'bg-gray-600'
                    }`}
                  >
                    <div className={`w-4 h-4 bg-white rounded-full transition-transform ${
                      account.status === 'enabled' ? 'translate-x-6' : 'translate-x-1'
                    }`}></div>
                  </button>
                </div>
              </div>

              {account.description && (
                <p className="text-gray-300 text-sm mb-4">{account.description}</p>
              )}

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Status:</span>
                  <span className={`font-medium ${
                    account.status === 'enabled' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {account.status}
                  </span>
                </div>
                {account.last_posted && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Last Posted:</span>
                    <span className="text-gray-300">
                      {new Date(account.last_posted).toLocaleDateString()}
                    </span>
                  </div>
                )}
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(account)}
                  className="modern-button px-3 py-1 text-sm flex-1"
                >
                  Edit
                </button>
                <button
                  onClick={() => testSession(account.username)}
                  className="modern-button px-3 py-1 text-sm bg-blue-600 hover:bg-blue-700"
                >
                  Test Session
                </button>
                <button
                  onClick={() => handleDelete(account.id)}
                  className="modern-button px-3 py-1 text-sm bg-red-600 hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="modern-card p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-white">
                {editingAccount ? 'Edit Account' : 'Add New Account'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Username *
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  required
                  className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors"
                  placeholder="Enter Threads username"
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Password *
                </label>
                <input
                  type="password"
                  value={hidePassword ? '' : formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required={!editingAccount}
                  disabled={hidePassword}
                  className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors disabled:opacity-50"
                  placeholder={hidePassword ? "Password hidden for security" : (editingAccount ? "Leave blank to keep current password" : "Enter Threads password")}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  rows={3}
                  className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors resize-none"
                  placeholder="Account description (optional)"
                />
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-6 py-3 text-gray-300 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="modern-button px-6 py-3 glow-on-hover"
                >
                  {editingAccount ? 'Update Account' : 'Add Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 