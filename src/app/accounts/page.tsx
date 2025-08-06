'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { supabase } from '@/lib/supabase'

interface Account {
  id: number
  username: string
  email: string
  password: string
  description?: string
  posting_config: any
  fingerprint_config: any
  status: 'enabled' | 'disabled'
  created_at: string
}

export default function AccountsPage() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [editingAccount, setEditingAccount] = useState<Account | null>(null)
  
  // Form state
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    description: '',
    posting_config: '{}',
    fingerprint_config: '{}'
  })

  useEffect(() => {
    fetchAccounts()
  }, [])

  const fetchAccounts = async () => {
    try {
      const { data, error } = await supabase
        .from('accounts')
        .select('*')
        .order('created_at', { ascending: false })

      if (error) {
        setMessage('Error fetching accounts: ' + error.message)
      } else {
        setAccounts(data || [])
      }
    } catch (error) {
      setMessage('Error fetching accounts: ' + error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setMessage('')

    try {
      const accountData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        description: formData.description || null,
        posting_config: JSON.parse(formData.posting_config),
        fingerprint_config: JSON.parse(formData.fingerprint_config),
        status: 'enabled' as const,
        created_at: new Date().toISOString()
      }

      if (editingAccount) {
        // Update existing account
        const { error } = await supabase
          .from('accounts')
          .update(accountData)
          .eq('id', editingAccount.id)

        if (error) {
          setMessage('Error updating account: ' + error.message)
        } else {
          setMessage('Account updated successfully!')
          setIsModalOpen(false)
          setEditingAccount(null)
          resetForm()
          await fetchAccounts()
        }
      } else {
        // Create new account
        const { error } = await supabase
          .from('accounts')
          .insert([accountData])

        if (error) {
          setMessage('Error creating account: ' + error.message)
        } else {
          setMessage('Account created successfully!')
          setIsModalOpen(false)
          resetForm()
          await fetchAccounts()
        }
      }
    } catch (error) {
      setMessage('Error: ' + error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleEdit = (account: Account) => {
    setEditingAccount(account)
    setFormData({
      username: account.username,
      email: account.email,
      password: account.password,
      description: account.description || '',
      posting_config: JSON.stringify(account.posting_config, null, 2),
      fingerprint_config: JSON.stringify(account.fingerprint_config, null, 2)
    })
    setIsModalOpen(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this account?')) return

    try {
      const { error } = await supabase
        .from('accounts')
        .delete()
        .eq('id', id)

      if (error) {
        setMessage('Error deleting account: ' + error.message)
      } else {
        setMessage('Account deleted successfully!')
        await fetchAccounts()
      }
    } catch (error) {
      setMessage('Error deleting account: ' + error)
    }
  }

  const handleToggleStatus = async (account: Account) => {
    try {
      const newStatus = account.status === 'enabled' ? 'disabled' : 'enabled'
      const { error } = await supabase
        .from('accounts')
        .update({ status: newStatus })
        .eq('id', account.id)

      if (error) {
        setMessage('Error updating status: ' + error.message)
      } else {
        await fetchAccounts()
      }
    } catch (error) {
      setMessage('Error updating status: ' + error)
    }
  }

  const resetForm = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      description: '',
      posting_config: '{}',
      fingerprint_config: '{}'
    })
  }

  const openModal = () => {
    setEditingAccount(null)
    resetForm()
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setEditingAccount(null)
    resetForm()
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Threads Accounts</h1>
        <Button onClick={openModal} className="bg-blue-600 hover:bg-blue-700">
          Add Account
        </Button>
      </div>

      {message && (
        <div className={`mb-4 p-3 rounded ${
          message.includes('successfully') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {message}
        </div>
      )}

      {/* Accounts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {accounts.map((account) => (
          <Card key={account.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{account.username}</CardTitle>
                  <p className="text-sm text-gray-600">{account.email}</p>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  account.status === 'enabled' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {account.status}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {account.description && (
                <p className="text-sm text-gray-600 mb-3">{account.description}</p>
              )}
              
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm font-medium">Bot Status:</span>
                <Button
                  variant={account.status === 'enabled' ? 'default' : 'secondary'}
                  size="sm"
                  onClick={() => handleToggleStatus(account)}
                >
                  {account.status === 'enabled' ? 'Enabled' : 'Disabled'}
                </Button>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEdit(account)}
                  className="flex-1"
                >
                  Edit
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => handleDelete(account.id)}
                  className="flex-1"
                >
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {accounts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">No accounts found. Add your first Threads account!</p>
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">
                {editingAccount ? 'Edit Account' : 'Add New Account'}
              </h2>
              <Button variant="ghost" onClick={closeModal} size="sm">
                ✕
              </Button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="username">Username *</Label>
                  <Input
                    id="username"
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    required
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="email">Email *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    required
                    className="mt-1"
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="password">Password *</Label>
                <Input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  required
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  className="mt-1"
                  rows={2}
                />
              </div>

              <div>
                <Label htmlFor="posting_config">Posting Config JSON *</Label>
                <Textarea
                  id="posting_config"
                  value={formData.posting_config}
                  onChange={(e) => setFormData({...formData, posting_config: e.target.value})}
                  required
                  className="mt-1 font-mono text-sm"
                  rows={4}
                  placeholder='{"key": "value"}'
                />
              </div>

              <div>
                <Label htmlFor="fingerprint_config">Fingerprint Config JSON *</Label>
                <Textarea
                  id="fingerprint_config"
                  value={formData.fingerprint_config}
                  onChange={(e) => setFormData({...formData, fingerprint_config: e.target.value})}
                  required
                  className="mt-1 font-mono text-sm"
                  rows={4}
                  placeholder='{"key": "value"}'
                />
              </div>

              <div className="flex gap-3 pt-4">
                <Button type="submit" disabled={isLoading} className="flex-1">
                  {isLoading ? 'Saving...' : (editingAccount ? 'Update Account' : 'Add Account')}
                </Button>
                <Button type="button" variant="outline" onClick={closeModal} className="flex-1">
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 