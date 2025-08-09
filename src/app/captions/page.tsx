'use client'

import { useEffect, useState, useRef } from 'react'
import { 
  PlusIcon, 
  CloudArrowUpIcon,
  ArrowPathIcon,
  TrashIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline'
import { API_BASE } from '@/lib/config'
import GlassCard from '@/components/ui/GlassCard'
import GlassButton from '@/components/ui/GlassButton'
import StatusChip from '@/components/ui/StatusChip'
import GlassModal from '@/components/ui/GlassModal'

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
      const response = await fetch(`${API_BASE}/api/captions`)
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
      
      const response = await fetch(`${API_BASE}/api/captions`, {
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
      
      const response = await fetch(`${API_BASE}/api/captions/${editingCaption.id}`, {
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
      const response = await fetch(`${API_BASE}/api/captions/${captionId}`, {
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
      const response = await fetch(`${API_BASE}/api/captions/reset`, {
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
      
      const response = await fetch(`${API_BASE}/api/captions/upload`, {
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
          <h1 className="heading-1 gradient-text">Captions</h1>
          <p className="text-body mt-2">Manage your caption library for automated posting</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-2">
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
          
          <GlassButton
            variant="ghost"
            onClick={() => csvInputRef.current?.click()}
            disabled={csvUploading}
            loading={csvUploading}
          >
            <CloudArrowUpIcon className="w-5 h-5" />
            Upload CSV
          </GlassButton>
          
          <GlassButton
            variant="ghost"
            onClick={resetAllCaptions}
          >
            <ArrowPathIcon className="w-5 h-5" />
            Reset All
          </GlassButton>
          
          <GlassButton onClick={() => setShowModal(true)}>
            <PlusIcon className="w-5 h-5" />
            Add Caption
          </GlassButton>
        </div>
      </div>

      {/* Stats */}
      <div className="responsive-grid">
        <GlassCard dense className="animate-slide-up text-center">
          <p className="heading-3 text-white mb-1">{captions.length}</p>
          <p className="text-caption">Total Captions</p>
        </GlassCard>
        
        <GlassCard dense className="animate-slide-up text-center" style={{ animationDelay: '100ms' }}>
          <p className="heading-3 text-emerald-400 mb-1">{unusedCount}</p>
          <p className="text-caption">Unused</p>
        </GlassCard>
        
        <GlassCard dense className="animate-slide-up text-center" style={{ animationDelay: '200ms' }}>
          <p className="heading-3 text-blue-400 mb-1">{captions.length - unusedCount}</p>
          <p className="text-caption">Used</p>
        </GlassCard>
        
        <GlassCard dense className="animate-slide-up text-center" style={{ animationDelay: '300ms' }}>
          <p className="heading-3 text-primary mb-1">
            {captions.length > 0 ? Math.round((unusedCount / captions.length) * 100) : 0}%
          </p>
          <p className="text-caption">Available</p>
        </GlassCard>
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

      {/* Captions Grid */}
      <GlassCard 
        title="Caption Library" 
        subtitle={`${captions.length} total captions`}
        className="animate-slide-up"
      >
        {captions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-blob">
              <ChatBubbleLeftRightIcon className="w-8 h-8 text-primary" />
            </div>
            <h3 className="heading-4 text-white mb-2">No captions yet</h3>
            <p className="text-body mb-6">Add captions to start automated posting</p>
            <GlassButton onClick={() => setShowModal(true)}>
              Add Your First Caption
            </GlassButton>
          </div>
        ) : (
          <div className="responsive-grid">
            {captions.map((caption, index) => (
              <GlassCard
                key={caption.id}
                dense
                className={`animate-slide-up ${
                  caption.used 
                    ? 'border-amber-500/20 bg-amber-500/5' 
                    : 'border-emerald-500/20 bg-emerald-500/5'
                }`}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <StatusChip status={caption.used ? 'warning' : 'success'}>
                      {caption.used ? 'Used' : 'Available'}
                    </StatusChip>
                    <div className="flex gap-1">
                      <GlassButton
                        variant="ghost"
                        size="sm"
                        onClick={() => openEditModal(caption)}
                        className="!p-1"
                      >
                        <PencilIcon className="w-4 h-4" />
                      </GlassButton>
                      <GlassButton
                        variant="danger"
                        size="sm"
                        onClick={() => deleteCaption(caption.id)}
                        className="!p-1"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </GlassButton>
                    </div>
                  </div>
                  
                  {/* Caption Text */}
                  <p className="text-body text-sm overflow-hidden" style={{
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical'
                  }}>
                    {caption.text}
                  </p>
                  
                  {/* Category */}
                  {caption.category && (
                    <p className="text-xs text-blue-400">
                      Category: {caption.category}
                    </p>
                  )}
                  
                  {/* Tags */}
                  {caption.tags && caption.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {caption.tags.slice(0, 3).map((tag, tagIndex) => (
                        <span key={tagIndex} className="text-xs bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full">
                          #{tag}
                        </span>
                      ))}
                      {caption.tags.length > 3 && (
                        <span className="text-xs text-white/60">
                          +{caption.tags.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                  
                  {/* Timestamps */}
                  <div className="text-xs text-caption space-y-1">
                    <p>Added {new Date(caption.created_at).toLocaleDateString()}</p>
                    {caption.used_at && (
                      <p>Used {new Date(caption.used_at).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </GlassCard>

      {/* Add/Edit Caption Modal */}
      <GlassModal
        isOpen={showModal}
        onClose={() => { setShowModal(false); resetForm(); }}
        title={editingCaption ? 'Edit Caption' : 'Add Caption'}
        size="lg"
      >
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Caption Text *
            </label>
            <textarea
              value={formData.text}
              onChange={(e) => setFormData({ ...formData, text: e.target.value })}
              placeholder="Write your caption here..."
              rows={4}
              className="glass-input resize-none"
              required
            />
            <p className="text-xs text-white/60 mt-1">
              {formData.text.length} characters
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Category
            </label>
            <input
              type="text"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              placeholder="e.g., motivation, lifestyle, business"
              className="glass-input"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Tags
            </label>
            <input
              type="text"
              value={formData.tags}
              onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
              placeholder="tag1, tag2, tag3"
              className="glass-input"
            />
            <p className="text-xs text-white/60 mt-1">
              Separate tags with commas
            </p>
          </div>
          
          <div className="flex gap-3 pt-4">
            <GlassButton
              onClick={editingCaption ? updateCaption : createCaption}
              disabled={!formData.text.trim()}
              className="flex-1"
            >
              {editingCaption ? 'Update Caption' : 'Add Caption'}
            </GlassButton>
            <GlassButton
              variant="ghost"
              onClick={() => { setShowModal(false); resetForm(); }}
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