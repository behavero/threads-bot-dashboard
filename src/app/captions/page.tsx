'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'

interface Caption {
  id: number
  text: string
  category: string
  tags: string[]
  used: boolean
  created_at: string
}

interface CaptionFormData {
  text: string
  category: string
  tags: string
}

export default function CaptionsPage() {
  const { user } = useAuth()
  const [captions, setCaptions] = useState<Caption[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingCaption, setEditingCaption] = useState<Caption | null>(null)
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [isUploadingCsv, setIsUploadingCsv] = useState(false)
  const [formData, setFormData] = useState<CaptionFormData>({
    text: '',
    category: '',
    tags: ''
  })

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
    fetchCaptions()
  }, [])

  const fetchCaptions = async () => {
    try {
      console.log('Fetching captions...')
      const response = await fetch('/api/prompts')
      const data = await response.json()

      console.log('Captions response:', data)

      if (data.success) {
        // Ensure all captions have required properties with defaults
        const processedCaptions = data.prompts.map((caption: any) => ({
          id: caption.id,
          text: caption.text || '',
          category: caption.category || 'general',
          tags: Array.isArray(caption.tags) ? caption.tags : [],
          used: caption.used || false,
          created_at: caption.created_at || new Date().toISOString()
        }))
        console.log('Processed captions:', processedCaptions.length)
        setCaptions(processedCaptions)
        setError('') // Clear any previous errors
      } else {
        console.error('Failed to fetch captions:', data.error)
        setError(data.error || 'Failed to fetch captions')
        setCaptions([])
      }
    } catch (err) {
      console.error('Error fetching captions:', err)
      setError('Error fetching captions')
      setCaptions([])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const url = editingCaption
        ? `/api/prompts/${editingCaption.id}`
        : '/api/prompts'

      const method = editingCaption ? 'PUT' : 'POST'

      // Clean and validate form data
      const cleanedFormData = {
        text: formData.text.trim(),
        category: formData.category || 'general',
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
      }

      // Validate required fields
      if (!cleanedFormData.text) {
        setError('Caption text is required')
        return
      }

      console.log('Submitting caption data:', cleanedFormData)
      console.log('Request URL:', url)
      console.log('Request method:', method)

      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(cleanedFormData)
      })

      console.log('Response status:', response.status)
      
      const data = await response.json()
      console.log('Response data:', data)

      if (data.success) {
        setShowModal(false)
        setEditingCaption(null)
        resetForm()
        await fetchCaptions()
        setMessage(editingCaption ? 'Caption updated successfully!' : 'Caption added successfully!')
      } else {
        console.error('Failed to save caption:', data.error)
        setError(data.error || 'Failed to save caption')
      }
    } catch (err) {
      console.error('Error saving caption:', err)
      setError('Error saving caption')
    }
  }

  const handleEdit = (caption: Caption) => {
    setEditingCaption(caption)
    setFormData({
      text: caption.text || '',
      category: caption.category || 'general',
      tags: Array.isArray(caption.tags) ? caption.tags.join(', ') : ''
    })
    setShowModal(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this caption?')) return

    try {
      const response = await fetch(`/api/prompts/${id}`, {
        method: 'DELETE'
      })

      const data = await response.json()

      if (data.success) {
        await fetchCaptions()
      } else {
        setError(data.error || 'Failed to delete caption')
      }
    } catch (err) {
      setError('Error deleting caption')
    }
  }

  const handleCsvUpload = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!csvFile) return

    setIsUploadingCsv(true)
    setError('')
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', csvFile)

      console.log('Uploading CSV file:', csvFile.name)

      const response = await fetch('/api/prompts/upload-csv', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()
      console.log('CSV upload response:', data)

      if (data.success) {
        setCsvFile(null)
        await fetchCaptions()
        setMessage(data.message || `Successfully uploaded ${data.captions?.length || 0} captions`)
      } else {
        setError(data.error || 'Failed to upload CSV')
      }
    } catch (err) {
      console.error('CSV upload error:', err)
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

  const handleToggleUsed = async (caption: Caption) => {
    try {
      const response = await fetch(`/api/prompts/${caption.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...caption,
          used: !caption.used
        })
      })

      const data = await response.json()

      if (data.success) {
        await fetchCaptions()
      } else {
        setError(data.error || 'Failed to update caption status')
      }
    } catch (err) {
      setError('Error updating caption status')
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
    setEditingCaption(null)
    resetForm()
    setShowModal(true)
  }

  const filteredCaptions = captions.filter(caption =>
    selectedCategory === 'all' || caption.category === selectedCategory
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-2">Content Captions</h2>
          <p className="text-gray-300 text-sm sm:text-base">Manage your posting captions and content</p>
        </div>
        <button
          onClick={openAddModal}
          className="modern-button px-4 sm:px-6 py-2 sm:py-3 glow-on-hover w-full sm:w-auto"
        >
          Add Caption
        </button>
      </div>

      {/* Category Filter */}
      <div className="modern-card p-4 sm:p-6">
        <div className="flex flex-wrap gap-2">
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
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
          <div className="text-red-400 text-sm sm:text-base">{error}</div>
        </div>
      )}
      
      {message && (
        <div className="modern-card p-4 border border-green-500/30">
          <div className="text-green-400 text-sm sm:text-base">{message}</div>
        </div>
      )}

      {/* CSV Upload */}
      <div className="modern-card p-4 sm:p-6">
        <h3 className="text-lg sm:text-xl font-bold text-white mb-4">Bulk Upload Captions</h3>
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
              className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-transparent border border-gray-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs sm:file:text-sm file:font-medium file:bg-purple-600 file:text-white hover:file:bg-purple-700 transition-colors"
            />
            <p className="text-xs text-gray-400">
              CSV format: text,category,tags (one caption per line)
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
            className="modern-button px-4 sm:px-6 py-2 sm:py-3 glow-on-hover w-full sm:w-auto"
          >
            {isUploadingCsv ? 'Uploading...' : 'Upload CSV'}
          </button>
        </form>
      </div>

      {/* Captions Grid */}
      {filteredCaptions.length === 0 ? (
        <div className="modern-card p-8 sm:p-12 text-center">
          <div className="text-4xl sm:text-6xl mb-4">💬</div>
          <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">No Captions Yet</h3>
          <p className="text-gray-300 mb-6 text-sm sm:text-base">Add your first caption to start creating content</p>
          <button
            onClick={openAddModal}
            className="modern-button px-6 py-3 glow-on-hover"
          >
            Add Your First Caption
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 sm:gap-6">
          {filteredCaptions.map((caption) => (
            <div key={caption.id} className="modern-card p-4 sm:p-6 hover:scale-105 transition-transform duration-300">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1 min-w-0">
                  <h3 className="text-base sm:text-lg font-bold text-white mb-2 truncate">{caption.text.substring(0, 50)}...</h3>
                  <p className="text-gray-400 text-xs sm:text-sm">{caption.category}</p>
                </div>
                <div className="flex items-center space-x-2 ml-2">
                  <button
                    onClick={() => handleToggleUsed(caption)}
                    className={`w-10 sm:w-12 h-6 rounded-full transition-colors ${
                      caption.used
                        ? 'bg-green-500'
                        : 'bg-gray-600'
                    }`}
                  >
                    <div className={`w-3 sm:w-4 h-3 sm:h-4 bg-white rounded-full transition-transform ${
                      caption.used ? 'translate-x-4 sm:translate-x-6' : 'translate-x-1'
                    }`}></div>
                  </button>
                </div>
              </div>

              {caption.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-4">
                  {caption.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-purple-600/20 text-purple-300 text-xs rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="space-y-2 mb-4">
                <div className="flex justify-between text-xs sm:text-sm">
                  <span className="text-gray-400">Status:</span>
                  <span className={`font-medium ${
                    caption.used ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {caption.used ? 'Used' : 'Unused'}
                  </span>
                </div>
                <div className="flex justify-between text-xs sm:text-sm">
                  <span className="text-gray-400">Created:</span>
                  <span className="text-gray-300">
                    {new Date(caption.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => handleEdit(caption)}
                  className="modern-button px-3 py-1 text-xs sm:text-sm flex-1"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(caption.id)}
                  className="modern-button px-3 py-1 text-xs sm:text-sm bg-red-600 hover:bg-red-700"
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="modern-card p-6 sm:p-8 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl sm:text-2xl font-bold text-white">
                {editingCaption ? 'Edit Caption' : 'Add New Caption'}
              </h3>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-400 hover:text-white text-xl"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-300">
                  Caption Text *
                </label>
                <textarea
                  value={formData.text}
                  onChange={(e) => setFormData({...formData, text: e.target.value})}
                  required
                  rows={4}
                  className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors resize-none text-sm sm:text-base"
                  placeholder="Enter your caption text..."
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Category
                  </label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-transparent border border-gray-600 rounded-lg text-white focus:outline-none focus:border-purple-500 transition-colors text-sm sm:text-base"
                  >
                    <option value="general">General</option>
                    <option value="business">Business</option>
                    <option value="personal">Personal</option>
                    <option value="creative">Creative</option>
                    <option value="humor">Humor</option>
                    <option value="inspiration">Inspiration</option>
                    <option value="tech">Tech</option>
                    <option value="lifestyle">Lifestyle</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-gray-300">
                    Tags
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({...formData, tags: e.target.value})}
                    className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors text-sm sm:text-base"
                    placeholder="tag1, tag2, tag3"
                  />
                </div>
              </div>

              <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4 pt-4">
                <button
                  type="submit"
                  className="modern-button px-6 py-3 glow-on-hover flex-1"
                >
                  {editingCaption ? 'Update Caption' : 'Add Caption'}
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