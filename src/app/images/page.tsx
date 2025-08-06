'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth'

interface Image {
  id: number
  filename: string
  url: string
  size: number
  type: string
  created_at: string
}

export default function ImagesPage() {
  const { user } = useAuth()
  const [images, setImages] = useState<File[]>([])
  const [uploadedImages, setUploadedImages] = useState<Image[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [supabaseStatus, setSupabaseStatus] = useState<string>('')

  useEffect(() => {
    fetchUploadedImages()
    checkSupabaseConnection()
  }, [])

  const checkSupabaseConnection = async () => {
    try {
      const response = await fetch('/api/test-env')
      const data = await response.json()
      if (data.success && data.envVars.hasSupabaseUrl && data.envVars.hasSupabaseAnonKey) {
        setSupabaseStatus('Connected')
      } else {
        setSupabaseStatus('Config Error')
      }
    } catch (error) {
      setSupabaseStatus('Failed')
    }
  }

  const fetchUploadedImages = async () => {
    try {
      const response = await fetch('/api/upload')
      const data = await response.json()
      
      if (data.success) {
        setUploadedImages(data.data.images)
      }
    } catch (error) {
      console.error('Error fetching images:', error)
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileArray = Array.from(e.target.files)
      setImages(fileArray)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsUploading(true)
    setMessage('')

    try {
      const formData = new FormData()
      
      images.forEach(image => {
        formData.append('images', image)
      })

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (data.success) {
        setMessage('Upload successful!')
        setImages([])
        // Refresh the content list
        await fetchUploadedImages()
      } else {
        setMessage('Upload failed: ' + data.error)
      }
    } catch (error) {
      setMessage('Upload failed: ' + error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDeleteImage = async (id: number, filename: string) => {
    try {
      const response = await fetch(`/api/upload/images/${id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename })
      })
      
      if (response.ok) {
        setUploadedImages(prev => prev.filter(image => image.id !== id))
        setMessage('Image deleted successfully!')
      }
    } catch (error) {
      setMessage('Delete failed: ' + error)
    }
  }

  return (
    <div className="space-y-8">
      {/* Status Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">
            {supabaseStatus === 'Connected' ? '✓' : '✗'}
          </div>
          <div className="text-sm text-gray-300">Supabase Status</div>
          <div className="mt-4 w-8 h-8 bg-purple-500 rounded-full mx-auto opacity-60"></div>
        </div>
        
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{uploadedImages.length}</div>
          <div className="text-sm text-gray-300">Uploaded Images</div>
          <div className="mt-4 w-8 h-8 bg-green-500 rounded-full mx-auto opacity-60"></div>
        </div>
        
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{images.length}</div>
          <div className="text-sm text-gray-300">Selected Images</div>
          <div className="mt-4 w-8 h-8 bg-yellow-500 rounded-full mx-auto opacity-60"></div>
        </div>
      </div>

      {/* Upload Form */}
      <div className="modern-card p-8">
        <h3 className="text-2xl font-bold text-white mb-6">Upload Images</h3>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="images" className="text-sm font-medium text-gray-300">
              Select Images
            </label>
            <input
              id="images"
              type="file"
              multiple
              accept=".png,.jpg,.jpeg,.gif,.webp"
              onChange={handleImageChange}
              className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-600 file:text-white hover:file:bg-purple-700 transition-colors"
            />
            {images.length > 0 && (
              <div className="mt-2 text-sm text-gray-400">
                Selected {images.length} file(s): {images.map(img => img.name).join(', ')}
              </div>
            )}
          </div>
          
          {message && (
            <div className={`p-3 rounded-lg ${
              message.includes('successful') 
                ? 'bg-green-500/10 text-green-400 border border-green-500/30' 
                : 'bg-red-500/10 text-red-400 border border-red-500/30'
            }`}>
              {message}
            </div>
          )}
          
          <button 
            type="submit" 
            className="modern-button px-6 py-3 glow-on-hover" 
            disabled={isUploading || images.length === 0}
          >
            {isUploading ? 'Uploading...' : 'Upload Images'}
          </button>
        </form>
      </div>

      {/* Uploaded Images */}
      {uploadedImages.length > 0 && (
        <div className="modern-card p-8">
          <h3 className="text-2xl font-bold text-white mb-6">Uploaded Images</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {uploadedImages.map((image) => (
              <div key={image.id} className="relative group">
                <img
                  src={image.url}
                  alt={image.filename}
                  className="w-full h-48 object-cover rounded-lg border border-gray-700"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center rounded-lg">
                  <button
                    onClick={() => handleDeleteImage(image.id, image.filename)}
                    className="modern-button px-3 py-1 text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Delete
                  </button>
                </div>
                <div className="mt-2 text-xs text-gray-400">
                  {image.filename}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {uploadedImages.length === 0 && (
        <div className="modern-card p-12 text-center">
          <div className="text-6xl mb-4">🖼️</div>
          <h3 className="text-xl font-semibold text-white mb-2">No Images Yet</h3>
          <p className="text-gray-300 mb-6">Upload your first image to start building your content library</p>
        </div>
      )}
    </div>
  )
} 