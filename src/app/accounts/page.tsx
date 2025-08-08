'use client'

import { useState, useEffect } from 'react'
import ErrorBoundary from '@/components/ErrorBoundary'

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
  last_login?: string
}

interface AccountFormData {
  username: string
  password: string
  description: string
  verification_code?: string
}

interface LoginState {
  step: 'credentials' | 'verification' | 'success' | 'error'
  loading: boolean
  error: string
  message: string
  session_reused?: boolean
}

function AccountsPageContent() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  const [hidePassword, setHidePassword] = useState(false)
  const [loginState, setLoginState] = useState<LoginState>({
    step: 'credentials',
    loading: false,
    error: '',
    message: ''
  })
  const [requiresVerification, setRequiresVerification] = useState(false)
  const [verificationUsername, setVerificationUsername] = useState('')
  const [formData, setFormData] = useState<AccountFormData>({
    username: '',
    password: '',
    description: '',
    verification_code: ''
  })

  useEffect(() => {
    fetchAccounts()
  }, [])

  useEffect(() => {
    console.log('🔍 Modal render check:', { requiresVerification, showModal })
  }, [requiresVerification, showModal])

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
        // Show user-friendly error message
        const errorMessage = data.error || 'Failed to fetch accounts'
        setError(getUserFriendlyError(errorMessage))
        setAccounts([])
      }
    } catch (err) {
      console.error('Error fetching accounts:', err)
      setError('Network error. Please check your connection and try again.')
      setAccounts([])
    } finally {
      setIsLoading(false)
    }
  }

  const getUserFriendlyError = (error: string): string => {
    const errorLower = error.toLowerCase()
    
    if (errorLower.includes('database') || errorLower.includes('connection')) {
      return 'Database connection failed. Please try again.'
    }
    if (errorLower.includes('authentication') || errorLower.includes('credentials')) {
      return 'Authentication failed. Please check your credentials.'
    }
    if (errorLower.includes('instagram api') || errorLower.includes('threads api')) {
      return 'Instagram API not available. Please try again later.'
    }
    if (errorLower.includes('challenge') || errorLower.includes('verification')) {
      return 'Account verification required. Please check your email.'
    }
    if (errorLower.includes('checkpoint') || errorLower.includes('manual')) {
      return 'Account security check required. Please log in to Instagram/Threads manually first.'
    }
    if (errorLower.includes('2fa') || errorLower.includes('two-factor')) {
      return 'Two-factor authentication required. Please complete 2FA verification.'
    }
    if (errorLower.includes('blacklist') || errorLower.includes('ip')) {
      return 'IP address blocked. Please try from a different network.'
    }
    if (errorLower.includes('eof') || errorLower.includes('reading a line')) {
      return 'Interactive verification required. Please check your email for a verification code.'
    }
    
    return error || 'An unexpected error occurred. Please try again.'
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoginState(prev => ({ ...prev, loading: true, error: '', message: '' }))

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
          setLoginState(prev => ({ ...prev, step: 'success', message: 'Account updated successfully!' }))
        } else {
          setLoginState(prev => ({ ...prev, step: 'error', error: data.error || 'Failed to update account' }))
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
            password: formData.password,
            verification_code: formData.verification_code
          })
        })

        const data = await response.json()
        console.log('Login response:', data)

        if (data.success) {
          setShowModal(false)
          resetForm()
          setRequiresVerification(false)
          setVerificationUsername('')
          await fetchAccounts()
          
          const message = data.session_reused 
            ? `Account connected successfully! (Session reused) ${data.user_info?.followers || 0} followers, ${data.user_info?.posts || 0} posts`
            : `Account created successfully! ${data.user_info?.followers || 0} followers, ${data.user_info?.posts || 0} posts`
          
          setLoginState(prev => ({ 
            ...prev, 
            step: 'success', 
            message,
            session_reused: data.session_reused
          }))
          setHidePassword(true) // Hide password for security
        } else if (data.requires_verification || data.status === 'challenge_required') {
          // Handle verification required
          console.log('📧 Verification required - showing modal')
          setRequiresVerification(true)
          setVerificationUsername(formData.username)
          setLoginState(prev => ({ 
            ...prev, 
            step: 'verification', 
            message: 'Please check your email for a 6-digit verification code and enter it below.'
          }))
          console.log('✅ Modal state set to true')
        } else {
          setLoginState(prev => ({ 
            ...prev, 
            step: 'error', 
            error: getUserFriendlyError(data.error || 'Failed to create account')
          }))
        }
      }
    } catch (err) {
      console.error('Error saving account:', err)
      setLoginState(prev => ({ 
        ...prev, 
        step: 'error', 
        error: 'Network error. Please check your connection and try again.'
      }))
    } finally {
      setLoginState(prev => ({ ...prev, loading: false }))
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
        setError(getUserFriendlyError(data.error || 'Failed to delete account'))
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.')
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
        setError(getUserFriendlyError(data.error || 'Failed to update account status'))
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.')
    }
  }

  const resetForm = () => {
    setFormData({
      username: '',
      password: '',
      description: '',
      verification_code: ''
    })
    setHidePassword(false)
    setRequiresVerification(false)
    setVerificationUsername('')
    setLoginState({
      step: 'credentials',
      loading: false,
      error: '',
      message: ''
    })
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
        setError(getUserFriendlyError(data.error || 'Login test failed'))
      }
    } catch (err) {
      console.error('Login test error:', err)
      setError('Network error. Please check your connection and try again.')
    }
  }

  const testThreadsAPI = async () => {
    try {
      setError('')
      console.log('Testing Threads API...')
      
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/accounts/test-threads-login', {
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
      console.log('Threads API test response:', data)
      
      if (data.success) {
        setMessage('Threads API test successful! API is available and working.')
      } else {
        if (data.api_available === false) {
          setError('Threads API not available. Check backend dependencies.')
        } else {
          setError(getUserFriendlyError(data.error || 'Threads API test failed'))
        }
      }
    } catch (err) {
      console.error('Threads API test error:', err)
      setError('Network error. Please check your connection and try again.')
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
        setError(getUserFriendlyError(data.error || 'Session test failed'))
      }
    } catch (err) {
      console.error('Session test error:', err)
      setError('Network error. Please check your connection and try again.')
    }
  }

  const postNow = async (accountId: number, username: string) => {
    try {
      setError('')
      setMessage('')
      console.log(`Triggering post for account ${username}...`)
      
      const response = await fetch(`https://threads-bot-dashboard-3.onrender.com/api/accounts/${accountId}/post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      const data = await response.json()
      console.log('Post response:', data)
      
      if (data.success) {
        setMessage(`Post published successfully for ${username}! ${data.session_reused ? '(Session reused)' : '(Fresh login)'}`)
        // Refresh accounts to update last_posted
        await fetchAccounts()
      } else {
        setError(getUserFriendlyError(data.error || 'Failed to publish post'))
      }
    } catch (err) {
      console.error('Post error:', err)
      setError('Network error. Please check your connection and try again.')
    }
  }

  const testVerificationModal = async () => {
    console.log('🧪 Testing verification modal...')
    setRequiresVerification(true)
    setVerificationUsername('test_user')
    setMessage('Test: Verification modal should appear')
  }

  const testBackendVerificationResponse = async () => {
    console.log('🧪 Testing backend verification response...')
    
    // Simulate the backend response that should trigger verification
    const mockResponse = {
      success: false,
      requires_verification: true,
      verification_type: "email",
      message: "Email verification required",
      error: "Please check your email for a 6-digit verification code"
    }
    
    console.log('📧 Mock response:', mockResponse)
    
    if (mockResponse.requires_verification) {
      console.log('📧 Verification required - showing modal')
      setRequiresVerification(true)
      setVerificationUsername('Lanavalentine.official')
      setMessage('Please check your email for a 6-digit verification code and enter it below.')
      console.log('✅ Modal state set to true')
    }
  }

  const submitVerificationCode = async (code: string) => {
    try {
      setError('')
      setMessage('')
      console.log(`Submitting verification code for ${verificationUsername}...`)
      
      // Try the new challenge verification endpoint first
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/accounts/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          username: verificationUsername,
          password: '', // Password not needed for verification
          verification_code: code
        })
      })
      
      const data = await response.json()
      console.log('Verification response:', data)
      
      if (data.success) {
        setRequiresVerification(false)
        setVerificationUsername('')
        setMessage(`Account verified successfully! ${data.user_info?.followers || 0} followers, ${data.user_info?.posts || 0} posts`)
        await fetchAccounts()
      } else {
        // Fallback to old verification endpoint
        const fallbackResponse = await fetch('https://threads-bot-dashboard-3.onrender.com/api/accounts/verify-code', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            username: verificationUsername,
            verification_code: code
          })
        })
        
        const fallbackData = await fallbackResponse.json()
        console.log('Fallback verification response:', fallbackData)
        
        if (fallbackData.success) {
          setRequiresVerification(false)
          setVerificationUsername('')
          setMessage(`Account verified successfully! ${fallbackData.user_info?.followers || 0} followers, ${fallbackData.user_info?.posts || 0} posts`)
          await fetchAccounts()
        } else {
          setError(getUserFriendlyError(fallbackData.error || 'Verification failed'))
        }
      }
    } catch (err) {
      console.error('Verification error:', err)
      setError('Network error. Please check your connection and try again.')
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
            onClick={testThreadsAPI}
            className="modern-button px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700"
          >
            Test Threads API
          </button>
          <button
            onClick={testVerificationModal}
            className="modern-button px-4 py-2 text-sm bg-purple-600 hover:bg-purple-700"
          >
            Test Verification Modal
          </button>
          <button
            onClick={testBackendVerificationResponse}
            className="modern-button px-4 py-2 text-sm bg-orange-600 hover:bg-orange-700"
          >
            Test Backend Response
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
                {account.last_login && (
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-400">Last Login:</span>
                    <span className="text-gray-300">
                      {new Date(account.last_login).toLocaleDateString()}
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
                  onClick={() => postNow(account.id, account.username)}
                  className="modern-button px-3 py-1 text-sm bg-green-600 hover:bg-green-700"
                >
                  Post Now
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
              {/* Step 1: Credentials */}
              {loginState.step === 'credentials' && (
                <>
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">
                      Username *
                    </label>
                    <input
                      type="text"
                      value={formData.username}
                      onChange={(e) => setFormData({...formData, username: e.target.value})}
                      required
                      disabled={loginState.loading}
                      className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors disabled:opacity-50"
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
                      disabled={hidePassword || loginState.loading}
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
                      disabled={loginState.loading}
                      className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors resize-none disabled:opacity-50"
                      placeholder="Account description (optional)"
                    />
                  </div>
                </>
              )}

              {/* Step 2: Verification */}
              {loginState.step === 'verification' && (
                <div className="space-y-4">
                  <div className="text-center">
                    <div className="text-6xl mb-4">📧</div>
                    <h4 className="text-lg font-semibold text-white mb-2">Email Verification Required</h4>
                    <p className="text-gray-300">
                      Please check your email for a 6-digit verification code from Instagram/Threads
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-gray-300">
                      Verification Code *
                    </label>
                    <input
                      type="text"
                      value={formData.verification_code}
                      onChange={(e) => setFormData({...formData, verification_code: e.target.value})}
                      required
                      maxLength={6}
                      disabled={loginState.loading}
                      className="w-full px-4 py-3 bg-transparent border border-purple-500 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors text-center text-2xl tracking-widest disabled:opacity-50"
                      placeholder="000000"
                    />
                  </div>
                </div>
              )}

              {/* Step 3: Success */}
              {loginState.step === 'success' && (
                <div className="text-center space-y-4">
                  <div className="text-6xl mb-4">✅</div>
                  <h4 className="text-lg font-semibold text-white mb-2">Account Connected Successfully!</h4>
                  <p className="text-gray-300">
                    {loginState.message}
                  </p>
                  {loginState.session_reused && (
                    <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-3">
                      <p className="text-green-400 text-sm">Session reused - no new login required</p>
                    </div>
                  )}
                </div>
              )}

              {/* Step 4: Error */}
              {loginState.step === 'error' && (
                <div className="text-center space-y-4">
                  <div className="text-6xl mb-4">❌</div>
                  <h4 className="text-lg font-semibold text-white mb-2">Login Failed</h4>
                  <p className="text-red-400">
                    {loginState.error}
                  </p>
                </div>
              )}

              {/* Loading State */}
              {loginState.loading && (
                <div className="text-center space-y-4">
                  <div className="text-6xl mb-4">⏳</div>
                  <h4 className="text-lg font-semibold text-white mb-2">Connecting Account...</h4>
                  <p className="text-gray-300">
                    Please wait while we connect to Threads
                  </p>
                </div>
              )}

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  disabled={loginState.loading}
                  className="px-6 py-3 text-gray-300 hover:text-white transition-colors disabled:opacity-50"
                >
                  Cancel
                </button>
                {loginState.step === 'credentials' && (
                  <button
                    type="submit"
                    disabled={loginState.loading}
                    className="modern-button px-6 py-3 glow-on-hover disabled:opacity-50"
                  >
                    {loginState.loading ? 'Connecting...' : (editingAccount ? 'Update Account' : 'Add Account')}
                  </button>
                )}
                {loginState.step === 'verification' && (
                  <button
                    type="submit"
                    disabled={loginState.loading || !formData.verification_code || formData.verification_code.length !== 6}
                    className="modern-button px-6 py-3 glow-on-hover disabled:opacity-50"
                  >
                    {loginState.loading ? 'Verifying...' : 'Verify Account'}
                  </button>
                )}
                {loginState.step === 'success' && (
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="modern-button px-6 py-3 glow-on-hover"
                  >
                    Done
                  </button>
                )}
                {loginState.step === 'error' && (
                  <button
                    type="button"
                    onClick={() => setLoginState(prev => ({ ...prev, step: 'credentials' }))}
                    className="modern-button px-6 py-3 glow-on-hover"
                  >
                    Try Again
                  </button>
                )}
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Verification Modal */}
      {requiresVerification && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="modern-card p-8 w-full max-w-md">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-2xl font-bold text-white">
                Email Verification Required
              </h3>
              <button
                onClick={() => {
                  setRequiresVerification(false)
                  setVerificationUsername('')
                }}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-6">
              <div className="text-center">
                <p className="text-gray-300 mb-4">
                  Please check your email for a 6-digit verification code from Instagram/Threads for account <strong>{verificationUsername}</strong>
                </p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Verification Code *
                </label>
                <input
                  type="text"
                  id="verification-code"
                  maxLength={6}
                  className="w-full px-4 py-3 bg-transparent border border-purple-500 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors text-center text-2xl tracking-widest"
                  placeholder="000000"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const code = (e.target as HTMLInputElement).value
                      if (code.length === 6) {
                        submitVerificationCode(code)
                      }
                    }
                  }}
                />
              </div>

              <div className="flex justify-end space-x-4 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setRequiresVerification(false)
                    setVerificationUsername('')
                  }}
                  className="px-6 py-3 text-gray-300 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const code = (document.getElementById('verification-code') as HTMLInputElement)?.value
                    if (code && code.length === 6) {
                      submitVerificationCode(code)
                    }
                  }}
                  className="modern-button px-6 py-3 glow-on-hover"
                >
                  Verify Account
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="w-full border-t border-gray-700 py-4 text-center text-sm text-gray-400 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <a href="/privacy" className="hover:underline text-purple-400">Privacy Policy</a>
          {' '}•{' '}
          <a href="/terms" className="hover:underline text-purple-400">Terms of Service</a>
          {' '}•{' '}
          <span>© 2025 Threadly. All rights reserved.</span>
        </div>
      </footer>
    </div>
  )
}

export default function AccountsPage() {
  return (
    <ErrorBoundary>
      <AccountsPageContent />
    </ErrorBoundary>
  )
} 