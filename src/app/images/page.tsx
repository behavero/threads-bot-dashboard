'use client'

import { useEffect, useState, useRef } from 'react'
import { 
  PlusIcon, 
  CloudArrowUpIcon,
  LinkIcon,
  TrashIcon,
  EyeIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  PhotoIcon
} from '@heroicons/react/24/outline'
import { API_BASE } from '@/lib/config'
import GlassCard from '@/components/ui/GlassCard'
import GlassButton from '@/components/ui/GlassButton'
import StatusChip from '@/components/ui/StatusChip'
import GlassModal from '@/components/ui/GlassModal'

interface Image {
  id: number
  filename: string
  url: string
  alt_text: string | null
  use_count: number
  created_at: string
  last_used_at: string | null
}

interface ImageFormData {
  url: string
  alt_text: string
}

export default function ImagesPage() {
  const [images, setImages] = useState<Image[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [modalType, setModalType] = useState<'upload' | 'url'>('upload')
  const [formData, setFormData] = useState<ImageFormData>({
    url: '',
    alt_text: ''
  })
  const [uploading, setUploading] = useState(false)
  const [previewImage, setPreviewImage] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchImages()
  }, [])

  const fetchImages = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE}/api/images`)
      const data = await response.json()
      
      if (data.ok) {
        setImages(data.images || [])
      } else {
        setError(data.error || 'Failed to fetch images')
      }
    } catch (err) {
      setError('Failed to connect to server')
    } finally {
      setLoading(false)
    }
  }

  const uploadFile = async (file: File) => {
    try {
      setUploading(true)
      
      const uploadFormData = new FormData()
      uploadFormData.append('image_file', file)
      uploadFormData.append('alt_text', formData.alt_text || '')
      
      const response = await fetch(`${API_BASE}/api/images/upload`, {
        method: 'POST',
        body: uploadFormData
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage('Image uploaded successfully!')
        setShowModal(false)
        resetForm()
        await fetchImages()
      } else {
        setError(data.error || 'Failed to upload image')
      }
    } catch (err) {
      setError('Failed to upload image')
    } finally {
      setUploading(false)
    }
  }

  const addImageByUrl = async () => {
    try {
      setUploading(true)
      
      const response = await fetch(`${API_BASE}/api/images`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: formData.url,
          alt_text: formData.alt_text || null
        })
      })
      
      const data = await response.json()
      
      if (data.ok) {
        setMessage('Image added successfully!')
        setShowModal(false)
        resetForm()
        await fetchImages()
      } else {
        setError(data.error || 'Failed to add image')
      }
    } catch (err) {
      setError('Failed to add image')
    } finally {
      setUploading(false)
    }
  }

  const deleteImage = async (imageId: number) => {
    if (!confirm('Are you sure you want to delete this image?')) return
    
    try {
      const response = await fetch(`${API_BASE}/api/images/${imageId}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        setMessage('Image deleted successfully!')
        await fetchImages()
      } else {
        setError('Failed to delete image')
      }
    } catch (err) {
      setError('Failed to delete image')
    }
  }

  const openModal = (type: 'upload' | 'url') => {
    setModalType(type)
    setShowModal(true)
    resetForm()
  }

  const resetForm = () => {
    setFormData({ url: '', alt_text: '' })
    setPreviewImage(null)
    setError('')
    setMessage('')
  }

  const handleFileSelect = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onload = (e) => setPreviewImage(e.target?.result as string)
      reader.readAsDataURL(file)
      
      // Auto-set alt text from filename
      const filename = file.name.split('.')[0]
      setFormData(prev => ({ ...prev, alt_text: filename.replace(/[_-]/g, ' ') }))
    }
  }

  const totalUseCount = images.reduce((sum, img) => sum + img.use_count, 0)
  const averageUseCount = images.length > 0 ? Math.round(totalUseCount / images.length) : 0

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
          <h1 className="heading-1 gradient-text">Images</h1>
          <p className="text-body mt-2">Manage your image library for automated posting</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-2">
          <GlassButton
            variant="ghost"
            onClick={() => openModal('url')}
          >
            <LinkIcon className="w-5 h-5" />
            Add URL
          </GlassButton>
          
          <GlassButton onClick={() => openModal('upload')}>
            <CloudArrowUpIcon className="w-5 h-5" />
            Upload Image
          </GlassButton>
        </div>
      </div>

      {/* Stats */}
      <div className="responsive-grid">
        <GlassCard dense className="animate-slide-up text-center">
          <p className="heading-3 text-white mb-1">{images.length}</p>
          <p className="text-caption">Total Images</p>
        </GlassCard>
        
        <GlassCard dense className="animate-slide-up text-center" style={{ animationDelay: '100ms' }}>
          <p className="heading-3 text-blue-400 mb-1">{totalUseCount}</p>
          <p className="text-caption">Total Uses</p>
        </GlassCard>
        
        <GlassCard dense className="animate-slide-up text-center" style={{ animationDelay: '200ms' }}>
          <p className="heading-3 text-primary mb-1">{averageUseCount}</p>
          <p className="text-caption">Avg Uses</p>
        </GlassCard>
        
        <GlassCard dense className="animate-slide-up text-center" style={{ animationDelay: '300ms' }}>
          <p className="heading-3 text-emerald-400 mb-1">
            {images.filter(img => img.use_count === 0).length}
          </p>
          <p className="text-caption">Unused</p>
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

      {/* Images Grid */}
      <GlassCard 
        title="Image Library" 
        subtitle={`${images.length} total images`}
        className="animate-slide-up"
      >
        {images.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-blob">
              <PhotoIcon className="w-8 h-8 text-primary" />
            </div>
            <h3 className="heading-4 text-white mb-2">No images yet</h3>
            <p className="text-body mb-6">Upload or add images to enhance your posts</p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <GlassButton onClick={() => openModal('upload')}>
                Upload Image
              </GlassButton>
              <GlassButton variant="ghost" onClick={() => openModal('url')}>
                Add by URL
              </GlassButton>
            </div>
          </div>
        ) : (
          <div className="responsive-grid">
            {images.map((image, index) => (
              <GlassCard
                key={image.id}
                dense
                className="animate-slide-up overflow-hidden"
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <div className="space-y-3">
                  {/* Image */}
                  <div className="aspect-square relative bg-glass-100 rounded-2xl overflow-hidden">
                    <img
                      src={image.url}
                      alt={image.alt_text || image.filename}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.style.display = 'none'
                        const parent = target.parentElement
                        if (parent) {
                          parent.innerHTML = `
                            <div class="w-full h-full flex items-center justify-center">
                              <svg class="w-12 h-12 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                              </svg>
                            </div>
                          `
                        }
                      }}
                    />
                    
                    {/* Actions */}
                    <div className="absolute top-2 right-2 flex gap-1">
                      <GlassButton
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(image.url, '_blank')}
                        className="!p-1 !w-7 !h-7"
                      >
                        <EyeIcon className="w-3 h-3" />
                      </GlassButton>
                      <GlassButton
                        variant="danger"
                        size="sm"
                        onClick={() => deleteImage(image.id)}
                        className="!p-1 !w-7 !h-7"
                      >
                        <TrashIcon className="w-3 h-3" />
                      </GlassButton>
                    </div>
                    
                    {/* Use Count Badge */}
                    {image.use_count > 0 && (
                      <div className="absolute top-2 left-2">
                        <StatusChip status="info" className="text-xs">
                          {image.use_count} uses
                        </StatusChip>
                      </div>
                    )}
                  </div>
                  
                  {/* Image Info */}
                  <div className="space-y-2">
                    <p className="text-body text-sm font-medium truncate">
                      {image.filename}
                    </p>
                    
                    {image.alt_text && (
                      <p className="text-caption text-xs overflow-hidden" style={{
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical'
                      }}>
                        {image.alt_text}
                      </p>
                    )}
                    
                    <div className="flex items-center justify-between text-xs">
                      <p className="text-caption">
                        {new Date(image.created_at).toLocaleDateString()}
                      </p>
                      
                      {image.last_used_at && (
                        <p className="text-blue-400">
                          Used {new Date(image.last_used_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </GlassCard>
            ))}
          </div>
        )}
      </GlassCard>

      {/* Add Image Modal */}
      <GlassModal
        isOpen={showModal}
        onClose={() => { setShowModal(false); resetForm(); }}
        title={modalType === 'upload' ? 'Upload Image' : 'Add Image by URL'}
        size="md"
      >
        <div className="space-y-6">
          {modalType === 'upload' ? (
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileSelect(file)
                }}
                className="hidden"
              />
              
              <div
                onClick={() => fileInputRef.current?.click()}
                className="border-2 border-dashed border-glass-border rounded-2xl p-8 text-center cursor-pointer hover:border-primary/60 transition-colors glass-card bg-glass-100"
              >
                {previewImage ? (
                  <div className="space-y-4">
                    <img
                      src={previewImage}
                      alt="Preview"
                      className="w-32 h-32 object-cover rounded-2xl mx-auto"
                    />
                    <p className="text-caption">Click to select a different image</p>
                  </div>
                ) : (
                  <div>
                    <CloudArrowUpIcon className="w-12 h-12 text-white/60 mx-auto mb-4" />
                    <p className="text-body mb-2">Drop image here or click to browse</p>
                    <p className="text-caption">PNG, JPG, GIF up to 10MB</p>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">
                Image URL *
              </label>
              <input
                type="url"
                value={formData.url}
                onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                placeholder="https://example.com/image.jpg"
                className="glass-input"
                required
              />
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">
              Alt Text / Description
            </label>
            <input
              type="text"
              value={formData.alt_text}
              onChange={(e) => setFormData({ ...formData, alt_text: e.target.value })}
              placeholder="Describe the image for accessibility"
              className="glass-input"
            />
          </div>
          
          <div className="flex gap-3 pt-4">
            <GlassButton
              onClick={() => {
                if (modalType === 'upload' && fileInputRef.current?.files?.[0]) {
                  uploadFile(fileInputRef.current.files[0])
                } else if (modalType === 'url') {
                  addImageByUrl()
                }
              }}
              disabled={uploading || (modalType === 'url' && !formData.url)}
              loading={uploading}
              className="flex-1"
            >
              {modalType === 'upload' ? 'Upload Image' : 'Add Image'}
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