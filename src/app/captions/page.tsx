'use client'

import { useEffect, useState, useRef } from 'react'
import Layout from '@/components/Layout'
import { 
  PlusIcon, 
  CloudArrowUpIcon,
  ArrowPathIcon,
  TrashIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

interface Caption {
  id: number
  text: string
  category: string | null
  tags: string[] | null
  used: boolean
  created_at: string
  used_at: string | null
}

interface CaptionFormData {
  text: string
  category: string
  tags: string
}

export default function CaptionsPage() {
  const [captions, setCaptions] = useState<Caption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [editingCaption, setEditingCaption] = useState<Caption | null>(null)
  const [formData, setFormData] = useState<CaptionFormData>({
    text: '',
    category: '',
    tags: ''
  })
  const [csvUploading, setCsvUploading] = useState(false)
  const csvInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchCaptions()
  }, [])

  const fetchCaptions = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/captions`)
      const data = await response.json()
      
      if (data.ok) {
        setCaptions(data.captions || [])
      } else {
        setError(data.error || 'Failed to fetch captions')
      }
    } catch (err) {
      setError('Failed to connect to server')
    } finally {
      setLoading(false)
    }
  }

  const createCaption = async () => {
    try {
      const tags = formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : []
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/captions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: formData.text,
          category: formData.category || null,
          tags: tags.length > 0 ? tags : null
        })
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage('Caption added successfully!')
        setShowModal(false)
        resetForm()
        await fetchCaptions()
      } else {
        setError(data.error || 'Failed to add caption')
      }
    } catch (err) {
      setError('Failed to add caption')
    }
  }

  const updateCaption = async () => {
    if (!editingCaption) return
    
    try {
      const tags = formData.tags ? formData.tags.split(',').map(t => t.trim()).filter(Boolean) : []
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/captions/${editingCaption.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: formData.text,
          category: formData.category || null,
          tags: tags.length > 0 ? tags : null
        })
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage('Caption updated successfully!')
        setShowModal(false)
        setEditingCaption(null)
        resetForm()
        await fetchCaptions()
      } else {
        setError(data.error || 'Failed to update caption')
      }
    } catch (err) {
      setError('Failed to update caption')
    }
  }

  const deleteCaption = async (captionId: number) => {
    if (!confirm('Are you sure you want to delete this caption?')) return
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/captions/${captionId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setMessage('Caption deleted successfully!')
        await fetchCaptions()
      } else {
        setError('Failed to delete caption')
      }
    } catch (err) {
      setError('Failed to delete caption')
    }
  }

  const resetAllCaptions = async () => {
    if (!confirm('Are you sure you want to mark all captions as unused? This cannot be undone.')) return
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/captions/reset`, {
        method: 'POST'
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage('All captions marked as unused!')
        await fetchCaptions()
      } else {
        setError(data.error || 'Failed to reset captions')
      }
    } catch (err) {
      setError('Failed to reset captions')
    }
  }

  const uploadCsv = async (file: File) => {
    try {
      setCsvUploading(true)
      
      const formData = new FormData()
      formData.append('csv_file', file)
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/captions/upload`, {
        method: 'POST',
        body: formData
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage(`Successfully uploaded ${data.count} captions!`)
        await fetchCaptions()
      } else {
        setError(data.error || 'Failed to upload CSV')
      }
    } catch (err) {
      setError('Failed to upload CSV')
    } finally {
      setCsvUploading(false)
    }
  }

  const openEditModal = (caption: Caption) => {
    setEditingCaption(caption)
    setFormData({
      text: caption.text,
      category: caption.category || '',
      tags: caption.tags ? caption.tags.join(', ') : ''
    })
    setShowModal(true)
  }

  const resetForm = () => {
    setFormData({ text: '', category: '', tags: '' })
    setEditingCaption(null)
    setError('')
    setMessage('')
  }

  const unusedCount = captions.filter(c => !c.used).length

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
            <h1 className="text-3xl font-bold text-gray-900">Captions</h1>
            <p className="text-gray-600 mt-1">Manage your caption library for automated posting</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <input
              ref={csvInputRef}
              type="file"
              accept=".csv"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) uploadCsv(file)
              }}
              className="hidden"
            />
            
            <button
              onClick={() => csvInputRef.current?.click()}
              disabled={csvUploading}
              className="btn-secondary flex items-center space-x-2"
            >
              <CloudArrowUpIcon className="w-5 h-5" />
              <span>{csvUploading ? 'Uploading...' : 'Upload CSV'}</span>
            </button>
            
            <button
              onClick={resetAllCaptions}
              className="btn-ghost flex items-center space-x-2"
            >
              <ArrowPathIcon className="w-5 h-5" />
              <span>Reset All</span>
            </button>
            
            <button
              onClick={() => setShowModal(true)}
              className="btn-primary flex items-center space-x-2"
            >
              <PlusIcon className="w-5 h-5" />
              <span>Add Caption</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{captions.length}</p>
              <p className="text-sm text-gray-600">Total Captions</p>
            </div>
          </div>
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{unusedCount}</p>
              <p className="text-sm text-gray-600">Unused</p>
            </div>
          </div>
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{captions.length - unusedCount}</p>
              <p className="text-sm text-gray-600">Used</p>
            </div>
          </div>
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">
                {captions.length > 0 ? Math.round((unusedCount / captions.length) * 100) : 0}%
              </p>
              <p className="text-sm text-gray-600">Available</p>
            </div>
          </div>
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

        {/* Captions Grid */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Caption Library</h2>
            <span className="text-sm text-gray-500">{captions.length} total</span>
          </div>

          {captions.length === 0 ? (
            <div className="text-center py-12">
              <PlusIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No captions yet</h3>
              <p className="text-gray-600 mb-4">Add captions to start automated posting</p>
              <button onClick={() => setShowModal(true)} className="btn-primary">
                Add Your First Caption
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {captions.map((caption) => (
                <div
                  key={caption.id}
                  className={`glass-card rounded-xl p-4 border ${
                    caption.used ? 'border-gray-200 bg-gray-50/50' : 'border-green-200 bg-green-50/30'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className={`badge ${caption.used ? 'badge-warning' : 'badge-success'}`}>
                      {caption.used ? 'Used' : 'Available'}
                    </span>
                    <div className="flex space-x-1">
                      <button
                        onClick={() => openEditModal(caption)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                      >
                        <PencilIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteCaption(caption.id)}
                        className="p-1 text-gray-400 hover:text-red-600"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-900 mb-3 overflow-hidden" style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {caption.text}
                  </p>
                  
                  {caption.category && (
                    <p className="text-xs text-blue-600 mb-1">
                      Category: {caption.category}
                    </p>
                  )}
                  
                  {caption.tags && caption.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-2">
                      {caption.tags.map((tag, index) => (
                        <span key={index} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  <p className="text-xs text-gray-500">
                    Added {new Date(caption.created_at).toLocaleDateString()}
                  </p>
                  
                  {caption.used_at && (
                    <p className="text-xs text-gray-500">
                      Used {new Date(caption.used_at).toLocaleDateString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add/Edit Caption Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="card w-full max-w-2xl max-h-[90vh] overflow-y-auto">
              <div className="card-header">
                <h3 className="card-title">
                  {editingCaption ? 'Edit Caption' : 'Add Caption'}
                </h3>
                <button onClick={() => { setShowModal(false); resetForm(); }}>
                  <XMarkIcon className="w-6 h-6 text-gray-400" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Caption Text *
                  </label>
                  <textarea
                    value={formData.text}
                    onChange={(e) => setFormData({ ...formData, text: e.target.value })}
                    placeholder="Write your caption here..."
                    rows={4}
                    className="form-input resize-none"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {formData.text.length} characters
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <input
                    type="text"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    placeholder="e.g., motivation, lifestyle, business"
                    className="form-input"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    placeholder="tag1, tag2, tag3"
                    className="form-input"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Separate tags with commas
                  </p>
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={editingCaption ? updateCaption : createCaption}
                    className="btn-primary flex-1"
                    disabled={!formData.text.trim()}
                  >
                    {editingCaption ? 'Update Caption' : 'Add Caption'}
                  </button>
                  <button
                    onClick={() => { setShowModal(false); resetForm(); }}
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