'use client'

import { useEffect, useState, useRef } from 'react'
import Layout from '@/components/Layout'
import { 
  PlusIcon, 
  CloudArrowUpIcon,
  LinkIcon,
  TrashIcon,
  EyeIcon,
  CheckIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline'

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
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/images`)
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
      
      const formData = new FormData()
      formData.append('image_file', file)
      formData.append('alt_text', formData.alt_text || '')
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/images/upload`, {
        method: 'POST',
        body: formData
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
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/images`, {
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
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/api/images/${imageId}`, {
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
            <h1 className="text-3xl font-bold text-gray-900">Images</h1>
            <p className="text-gray-600 mt-1">Manage your image library for automated posting</p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={() => openModal('url')}
              className="btn-secondary flex items-center space-x-2"
            >
              <LinkIcon className="w-5 h-5" />
              <span>Add URL</span>
            </button>
            
            <button
              onClick={() => openModal('upload')}
              className="btn-primary flex items-center space-x-2"
            >
              <CloudArrowUpIcon className="w-5 h-5" />
              <span>Upload Image</span>
            </button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-900">{images.length}</p>
              <p className="text-sm text-gray-600">Total Images</p>
            </div>
          </div>
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{totalUseCount}</p>
              <p className="text-sm text-gray-600">Total Uses</p>
            </div>
          </div>
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{averageUseCount}</p>
              <p className="text-sm text-gray-600">Avg Uses</p>
            </div>
          </div>
          <div className="card">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {images.filter(img => img.use_count === 0).length}
              </p>
              <p className="text-sm text-gray-600">Unused</p>
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

        {/* Images Grid */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Image Library</h2>
            <span className="text-sm text-gray-500">{images.length} total</span>
          </div>

          {images.length === 0 ? (
            <div className="text-center py-12">
              <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No images yet</h3>
              <p className="text-gray-600 mb-4">Upload or add images to enhance your posts</p>
              <div className="flex justify-center space-x-3">
                <button onClick={() => openModal('upload')} className="btn-primary">
                  Upload Image
                </button>
                <button onClick={() => openModal('url')} className="btn-secondary">
                  Add by URL
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {images.map((image) => (
                <div
                  key={image.id}
                  className="glass-card rounded-xl overflow-hidden border border-gray-200"
                >
                  <div className="aspect-square relative bg-gray-100">
                    <img
                      src={image.url}
                      alt={image.alt_text || image.filename}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xMDAgMTAwTDEwMCAxMDBaIiBzdHJva2U9IiM5Q0E5QjQiIHN0cm9rZS13aWR0aD0iMiIvPgo8L3N2Zz4K'
                      }}
                    />
                    <div className="absolute top-2 right-2 flex space-x-1">
                      <button
                        onClick={() => window.open(image.url, '_blank')}
                        className="p-1 bg-black bg-opacity-50 rounded text-white hover:bg-opacity-70"
                      >
                        <EyeIcon className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => deleteImage(image.id)}
                        className="p-1 bg-black bg-opacity-50 rounded text-white hover:bg-opacity-70"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </button>
                    </div>
                    
                    {image.use_count > 0 && (
                      <div className="absolute top-2 left-2">
                        <span className="bg-blue-500 text-white text-xs px-2 py-1 rounded">
                          {image.use_count} uses
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="p-3">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {image.filename}
                    </p>
                    
                    {image.alt_text && (
                      <p className="text-xs text-gray-600 mt-1 line-clamp-2">
                        {image.alt_text}
                      </p>
                    )}
                    
                    <div className="flex items-center justify-between mt-2">
                      <p className="text-xs text-gray-500">
                        {new Date(image.created_at).toLocaleDateString()}
                      </p>
                      
                      {image.last_used_at && (
                        <p className="text-xs text-blue-600">
                          Last used {new Date(image.last_used_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add Image Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="card w-full max-w-lg max-h-[90vh] overflow-y-auto">
              <div className="card-header">
                <h3 className="card-title">
                  {modalType === 'upload' ? 'Upload Image' : 'Add Image by URL'}
                </h3>
                <button onClick={() => { setShowModal(false); resetForm(); }}>
                  <XMarkIcon className="w-6 h-6 text-gray-400" />
                </button>
              </div>
              
              <div className="space-y-4">
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
                      className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center cursor-pointer hover:border-blue-400 transition-colors"
                    >
                      {previewImage ? (
                        <div className="space-y-4">
                          <img
                            src={previewImage}
                            alt="Preview"
                            className="w-32 h-32 object-cover rounded-lg mx-auto"
                          />
                          <p className="text-sm text-gray-600">Click to select a different image</p>
                        </div>
                      ) : (
                        <div>
                          <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                          <p className="text-lg text-gray-600 mb-2">Drop image here or click to browse</p>
                          <p className="text-sm text-gray-500">PNG, JPG, GIF up to 10MB</p>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Image URL *
                    </label>
                    <input
                      type="url"
                      value={formData.url}
                      onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                      placeholder="https://example.com/image.jpg"
                      className="form-input"
                      required
                    />
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Alt Text / Description
                  </label>
                  <input
                    type="text"
                    value={formData.alt_text}
                    onChange={(e) => setFormData({ ...formData, alt_text: e.target.value })}
                    placeholder="Describe the image for accessibility"
                    className="form-input"
                  />
                </div>
                
                <div className="flex space-x-3 pt-4">
                  <button
                    onClick={() => {
                      if (modalType === 'upload' && fileInputRef.current?.files?.[0]) {
                        uploadFile(fileInputRef.current.files[0])
                      } else if (modalType === 'url') {
                        addImageByUrl()
                      }
                    }}
                    className="btn-primary flex-1"
                    disabled={uploading || (modalType === 'url' && !formData.url)}
                  >
                    {uploading ? 'Processing...' : modalType === 'upload' ? 'Upload Image' : 'Add Image'}
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