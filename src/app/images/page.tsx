'use client'

import { useState, useEffect } from 'react'
import Image from 'next/image'

interface ImageFile {
  id: number
  filename: string
  url: string
  size: number
  type: string
  created_at: string
}

export default function ImagesPage() {
  const [images, setImages] = useState<ImageFile[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchUploadedImages()
  }, [])

  const fetchUploadedImages = async () => {
    try {
      console.log('Fetching uploaded images...')
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/images')
      const data = await response.json()
      
      console.log('Images response:', data)
      
      if (data.success) {
        setImages(data.images)
        console.log('Images loaded:', data.images.length)
      } else {
        console.error('Failed to fetch images:', data.error)
      }
    } catch (error) {
      console.error('Error fetching images:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileArray = Array.from(e.target.files)
      console.log('Selected images:', fileArray.map(f => ({ name: f.name, size: f.size, type: f.type })))
      setSelectedFiles(fileArray)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setUploading(true)
    setMessage('')

    try {
      const formData = new FormData()
      
      selectedFiles.forEach(image => {
        formData.append('images', image)
      })

      console.log('Uploading images:', selectedFiles.map(img => img.name))

      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/images', {
        method: 'POST',
        body: formData
      })

      console.log('Upload response status:', response.status)

      // Check if response is ok before trying to parse JSON
      if (!response.ok) {
        const errorText = await response.text()
        console.error('Server error response:', errorText)
        setMessage(`Upload failed: Server returned ${response.status} - ${errorText.substring(0, 100)}`)
        return
      }

      // Try to parse JSON response
      let data
      try {
        data = await response.json()
        console.log('Upload response data:', data)
      } catch (jsonError) {
        const responseText = await response.text()
        console.error('JSON parsing error:', jsonError)
        console.error('Response text:', responseText)
        setMessage(`Upload failed: Invalid JSON response - ${responseText.substring(0, 100)}`)
        return
      }

      if (data.success) {
        setMessage('Upload successful!')
        setSelectedFiles([])
        // Refresh the content list
        await fetchUploadedImages()
      } else {
        setMessage('Upload failed: ' + (data.error || 'Unknown error'))
      }
    } catch (error) {
      console.error('Upload error:', error)
      setMessage('Upload failed: ' + error)
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteImage = async (id: number, filename: string) => {
    if (!confirm('Are you sure you want to delete this image?')) return

    try {
      const response = await fetch(`https://threads-bot-dashboard-3.onrender.com/api/images/${id}`, {
        method: 'DELETE'
      })

      const data = await response.json()

      if (data.success) {
        await fetchUploadedImages()
      } else {
        setError(data.error || 'Failed to delete image')
      }
    } catch (error) {
      console.error('Error deleting image:', error)
      setError('Error deleting image')
    }
  }

  return (
    <div className="space-y-6 sm:space-y-8">
      {/* Status Indicators */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
        <div className="modern-card p-4 sm:p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-2xl sm:text-3xl font-bold gradient-text mb-2">
            {/* supabaseStatus === 'Connected' ? '✓' : '✗' */}
            {/* This variable is not defined in the new code, so it will be removed or commented out */}
            {/* For now, I'm keeping it as is, but it will cause a runtime error */}
            {/* <div className="text-2xl sm:text-3xl font-bold gradient-text mb-2">
              {supabaseStatus === 'Connected' ? '✓' : '✗'}
            </div> */}
            {/* <div className="text-xs sm:text-sm text-gray-300">Supabase Status</div> */}
          </div>
          <div className="text-xs sm:text-sm text-gray-300">Supabase Status</div>
        </div>
        
        <div className="modern-card p-4 sm:p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-2xl sm:text-3xl font-bold gradient-text mb-2">{images.length}</div>
          <div className="text-xs sm:text-sm text-gray-300">Uploaded Images</div>
        </div>
        
        <div className="modern-card p-4 sm:p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-2xl sm:text-3xl font-bold gradient-text mb-2">{selectedFiles.length}</div>
          <div className="text-xs sm:text-sm text-gray-300">Selected Images</div>
        </div>
      </div>

      {/* Upload Form */}
      <div className="modern-card p-6 sm:p-8">
        <h3 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6">Upload Images</h3>
        <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
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
              className="w-full px-3 sm:px-4 py-2 sm:py-3 bg-transparent border border-gray-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs sm:file:text-sm file:font-medium file:bg-purple-600 file:text-white hover:file:bg-purple-700 transition-colors"
            />
            {selectedFiles.length > 0 && (
              <div className="mt-2 text-xs sm:text-sm text-gray-400">
                Selected {selectedFiles.length} file(s): {selectedFiles.map(img => img.name).join(', ')}
              </div>
            )}
          </div>
          
          {message && (
            <div className={`p-3 rounded-lg text-sm sm:text-base ${
              message.includes('successful') 
                ? 'bg-green-500/10 text-green-400 border border-green-500/30' 
                : 'bg-red-500/10 text-red-400 border border-red-500/30'
            }`}>
              {message}
            </div>
          )}
          
          <button 
            type="submit" 
            className="modern-button px-4 sm:px-6 py-2 sm:py-3 glow-on-hover w-full sm:w-auto" 
            disabled={uploading || selectedFiles.length === 0}
          >
            {uploading ? 'Uploading...' : 'Upload Images'}
          </button>
        </form>
      </div>

      {/* Uploaded Images */}
      {images.length > 0 && (
        <div className="modern-card p-6 sm:p-8">
          <h3 className="text-xl sm:text-2xl font-bold text-white mb-4 sm:mb-6">Uploaded Images</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
            {images.map((image) => (
              <div key={image.id} className="relative group">
                <img
                  src={image.url}
                  alt={image.filename}
                  className="w-full h-32 sm:h-48 object-cover rounded-lg border border-gray-700"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center rounded-lg">
                  <button
                    onClick={() => handleDeleteImage(image.id, image.filename)}
                    className="modern-button px-3 py-1 text-xs sm:text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Delete
                  </button>
                </div>
                <div className="mt-2 text-xs text-gray-400 truncate">
                  {image.filename}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {images.length === 0 && (
        <div className="modern-card p-8 sm:p-12 text-center">
          <div className="text-4xl sm:text-6xl mb-4">🖼️</div>
          <h3 className="text-lg sm:text-xl font-semibold text-white mb-2">No Images Yet</h3>
          <p className="text-gray-300 mb-6 text-sm sm:text-base">Upload your first image to start building your content library</p>
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