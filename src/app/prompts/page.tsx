'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'

interface Prompt {
  id: number
  text: string
  category: string
  tags: string[]
  used: boolean
  created_at: string
}

interface PromptFormData {
  text: string
  category: string
  tags: string
}

export default function PromptsPage() {
  const { user } = useAuth()
  const [prompts, setPrompts] = useState<Prompt[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingPrompt, setEditingPrompt] = useState<Prompt | null>(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [formData, setFormData] = useState<PromptFormData>({
    text: '',
    category: '',
    tags: ''
  })
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [isUploadingCsv, setIsUploadingCsv] = useState(false)

  const categories = [
    'all',
    'general',
    'business',
    'personal',
    'creative',
    'humor',
    'inspiration',
    'tech',
    'lifestyle'
  ]

  useEffect(() => {
    fetchPrompts()
  }, [])

  const fetchPrompts = async () => {
    try {
      const response = await fetch('/api/prompts')
      const data = await response.json()
      
      if (data.success) {
        setPrompts(data.prompts)
      } else {
        setError(data.error || 'Failed to fetch prompts')
      }
    } catch (err) {
      setError('Error fetching prompts')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const url = editingPrompt 
        ? `/api/prompts/${editingPrompt.id}`
        : '/api/prompts'
      
      const method = editingPrompt ? 'PUT' : 'POST'
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        })
      })

      const data = await response.json()

      if (data.success) {
        setShowModal(false)
        setEditingPrompt(null)
        resetForm()
        await fetchPrompts()
      } else {
        setError(data.error || 'Failed to save prompt')
      }
    } catch (err) {
      setError('Error saving prompt')
    }
  }

  const handleEdit = (prompt: Prompt) => {
    setEditingPrompt(prompt)
    setFormData({
      text: prompt.text,
      category: prompt.category,
      tags: prompt.tags.join(', ')
    })
    setShowModal(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this prompt?')) return

    try {
      const response = await fetch(`/api/prompts/${id}`, {
        method: 'DELETE'
      })

      const data = await response.json()

      if (data.success) {
        await fetchPrompts()
      } else {
        setError(data.error || 'Failed to delete prompt')
      }
    } catch (err) {
      setError('Error deleting prompt')
    }
  }

  const handleCsvUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!csvFile) return

    setIsUploadingCsv(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', csvFile)

      const response = await fetch('/api/prompts/upload-csv', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (data.success) {
        setCsvFile(null)
        await fetchPrompts()
        setMessage(`Successfully uploaded ${data.count} prompts`)
      } else {
        setError(data.error || 'Failed to upload CSV')
      }
    } catch (err) {
      setError('Error uploading CSV')
    } finally {
      setIsUploadingCsv(false)
    }
  }

  const handleCsvChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCsvFile(e.target.files[0])
    }
  }

  const handleToggleUsed = async (prompt: Prompt) => {
    try {
      const response = await fetch(`/api/prompts/${prompt.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...prompt,
          used: !prompt.used
        })
      })

      const data = await response.json()

      if (data.success) {
        await fetchPrompts()
      } else {
        setError(data.error || 'Failed to update prompt status')
      }
    } catch (err) {
      setError('Error updating prompt status')
    }
  }

  const resetForm = () => {
    setFormData({
      text: '',
      category: '',
      tags: ''
    })
  }

  const openAddModal = () => {
    setEditingPrompt(null)
    resetForm()
    setShowModal(true)
  }

  const filteredPrompts = prompts.filter(prompt => 
    selectedCategory === 'all' || prompt.category === selectedCategory
  )

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
          <h2 className="text-3xl font-bold text-white mb-2">Content Prompts</h2>
          <p className="text-gray-300">Manage your posting prompts and captions</p>
        </div>
        <button
          onClick={openAddModal}
          className="modern-button px-6 py-3 glow-on-hover"
        >
          Add Prompt
        </button>
      </div>

      {/* Category Filter */}
      <div className="modern-card p-6">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedCategory === category
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

                   {/* Messages */}
             {error && (
               <div className="modern-card p-4 border border-red-500/30">
                 <div className="text-red-400">{error}</div>
               </div>
             )}
             
             {message && (
               <div className="modern-card p-4 border border-green-500/30">
                 <div className="text-green-400">{message}</div>
               </div>
             )}

             {/* CSV Upload */}
             <div className="modern-card p-6">
               <h3 className="text-xl font-bold text-white mb-4">Bulk Upload Prompts</h3>
               <form onSubmit={handleCsvUpload} className="space-y-4">
                 <div className="space-y-2">
                   <label htmlFor="csvFile" className="text-sm font-medium text-gray-300">
                     Upload CSV File
                   </label>
                   <input
                     id="csvFile"
                     type="file"
                     accept=".csv,.txt"
                     onChange={handleCsvChange}
                     className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-600 file:text-white hover:file:bg-purple-700 transition-colors"
                   />
                   <p className="text-xs text-gray-400">
                     CSV format: text,category,tags (one prompt per line)
                   </p>
                 </div>
                 
                 {csvFile && (
                   <div className="text-sm text-gray-300">
                     Selected file: {csvFile.name}
                   </div>
                 )}
                 
                 <button
                   type="submit"
                   disabled={!csvFile || isUploadingCsv}
                   className="modern-button px-6 py-3 glow-on-hover"
                 >
                   {isUploadingCsv ? 'Uploading...' : 'Upload CSV'}
                 </button>
               </form>
             </div>

      {/* Prompts Grid */}
      {filteredPrompts.length === 0 ? (
        <div className="modern-card p-12 text-center">
          <div className="text-6xl mb-4">💭</div>
          <h3 className="text-xl font-semibold text-white mb-2">No Prompts Yet</h3>
          <p className="text-gray-300 mb-6">Add your first prompt to start creating content</p>
          <button
            onClick={openAddModal}
            className="modern-button px-6 py-3 glow-on-hover"
          >
            Add Your First Prompt
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPrompts.map((prompt) => (
            <div key={prompt.id} className="modern-card p-6 hover:scale-105 transition-transform duration-300">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <p className="text-gray-300 text-sm mb-2 line-clamp-3">{prompt.text}</p>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      prompt.category === 'business' ? 'bg-blue-500/20 text-blue-400' :
                      prompt.category === 'personal' ? 'bg-green-500/20 text-green-400' :
                      prompt.category === 'creative' ? 'bg-purple-500/20 text-purple-400' :
                      prompt.category === 'humor' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {prompt.category}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      prompt.used ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                    }`}>
                      {prompt.used ? 'Used' : 'Unused'}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleToggleUsed(prompt)}
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                    prompt.used 
                      ? 'bg-green-500 text-white' 
                      : 'bg-gray-600 text-gray-400'
                  }`}
                >
                  {prompt.used ? '✓' : '○'}
                </button>
              </div>

              {prompt.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {prompt.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="flex justify-between items-center text-xs text-gray-500">
                <span>{new Date(prompt.created_at).toLocaleDateString()}</span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(prompt)}
                    className="modern-button px-2 py-1 text-xs"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(prompt.id)}
                    className="modern-button px-2 py-1 text-xs bg-red-600 hover:bg-red-700"
                  >
                    Delete
                  </button>
                </div>
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
                {editingPrompt ? 'Edit Prompt' : 'Add New Prompt'}
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
                  Prompt Text *
                </label>
                <textarea
                  value={formData.text}
                  onChange={(e) => setFormData({...formData, text: e.target.value})}
                  required
                  rows={4}
                  className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors resize-none"
                  placeholder="Enter your prompt text here..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500 transition-colors"
                  >
                    <option value="">Select category</option>
                    {categories.filter(cat => cat !== 'all').map((category) => (
                      <option key={category} value={category}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({...formData, tags: e.target.value})}
                    className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors"
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  type="submit"
                  className="modern-button px-6 py-3 glow-on-hover flex-1"
                >
                  {editingPrompt ? 'Update Prompt' : 'Add Prompt'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="modern-button px-6 py-3 bg-gray-600 hover:bg-gray-700"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
} 