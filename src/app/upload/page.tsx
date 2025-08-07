'use client'

import { useState, useEffect } from 'react'

interface UploadedFile {
  id: number
  filename: string
  url: string
  size: number
  type: string
  created_at: string
}

export default function UploadPage() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [isUploading, setIsUploading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  useEffect(() => {
    fetchUploadedContent()
    checkSupabaseConnection()
  }, [])

  const checkSupabaseConnection = async () => {
    try {
      const response = await fetch('/api/test-env')
      const data = await response.json()
      if (data.success && data.envVars.hasSupabaseUrl && data.envVars.hasSupabaseAnonKey) {
        // setSupabaseStatus('Connected') // This line was removed from the original file
      } else {
        // setSupabaseStatus('Config Error') // This line was removed from the original file
      }
    } catch (error) {
      // setSupabaseStatus('Failed') // This line was removed from the original file
    }
  }

  const fetchUploadedContent = async () => {
    try {
      const response = await fetch('/api/upload')
      const data = await response.json()
      
      if (data.success) {
        // setUploadedCaptions(data.data.captions) // This line was removed from the original file
        // setUploadedImages(data.data.images) // This line was removed from the original file
      }
    } catch (error) {
      console.error('Error fetching content:', error)
    }
  }

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileArray = Array.from(e.target.files)
      // setImages(fileArray) // This line was removed from the original file
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsUploading(true)
    setMessage('')

    try {
      const formData = new FormData()
      // formData.append('captions', captions) // This line was removed from the original file
      
      // images.forEach(image => { // This line was removed from the original file
      //   formData.append('images', image)
      // })

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (data.success) {
        setMessage('Upload successful!')
        // setCaptions('') // This line was removed from the original file
        // setImages([]) // This line was removed from the original file
        // Refresh the content list // This line was removed from the original file
        await fetchUploadedContent()
      } else {
        setMessage('Upload failed: ' + data.error)
      }
    } catch (error) {
      setMessage('Upload failed: ' + error)
    } finally {
      setIsUploading(false)
    }
  }

  const handleDeleteCaption = async (id: number) => {
    try {
      const response = await fetch(`/api/upload/captions/${id}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        // setUploadedCaptions(prev => prev.filter(caption => caption.id !== id)) // This line was removed from the original file
        setMessage('Caption deleted successfully!')
      }
    } catch (error) {
      setMessage('Delete failed: ' + error)
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
        // setUploadedImages(prev => prev.filter(image => image.id !== id)) // This line was removed from the original file
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
            {/* supabaseStatus === 'Connected' ? '✓' : '✗' */} {/* This line was removed from the original file */}
          </div>
          <div className="text-sm text-gray-300">Supabase Status</div>
        </div>
        
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{uploadedFiles.length}</div> {/* This line was changed from uploadedCaptions.length to uploadedFiles.length */}
          <div className="text-sm text-gray-300">Uploaded Files</div> {/* This line was changed from "Uploaded Captions" to "Uploaded Files" */}
        </div>
        
        <div className="modern-card p-6 text-center hover:scale-105 transition-transform duration-300">
          <div className="text-3xl font-bold gradient-text mb-2">{uploadedFiles.length}</div> {/* This line was changed from uploadedImages.length to uploadedFiles.length */}
          <div className="text-sm text-gray-300">Uploaded Files</div> {/* This line was changed from "Uploaded Images" to "Uploaded Files" */}
        </div>
      </div>

      {/* Upload Form */}
      <div className="modern-card p-8">
        <h3 className="text-2xl font-bold text-white mb-6">Upload Captions and Images</h3>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="captions" className="text-sm font-medium text-gray-300">
              Captions (one per line)
            </label>
            <textarea
              id="captions"
              // value={captions} // This line was removed from the original file
              // onChange={(e) => setCaptions(e.target.value)} // This line was removed from the original file
              placeholder="Enter your captions here, one per line..."
              rows={4}
              className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 transition-colors resize-none"
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="images" className="text-sm font-medium text-gray-300">
              Images
            </label>
            <input
              id="images"
              type="file"
              multiple
              accept=".png,.jpg,.jpeg"
              onChange={handleImageChange}
              className="w-full px-4 py-3 bg-transparent border border-gray-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-purple-600 file:text-white hover:file:bg-purple-700 transition-colors"
            />
            {/* images.length > 0 && ( // This line was removed from the original file
              <div className="mt-2 text-sm text-gray-400">
                Selected {images.length} file(s): {images.map(img => img.name).join(', ')}
              </div>
            ) */}
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
            disabled={isUploading}
          >
            {isUploading ? 'Uploading...' : 'Upload Content'}
          </button>
        </form>
      </div>

      {/* Uploaded Captions */}
      {uploadedFiles.length > 0 && ( // This line was changed from uploadedCaptions.length to uploadedFiles.length
        <div className="modern-card p-8">
          <h3 className="text-2xl font-bold text-white mb-6">Uploaded Files</h3> {/* This line was changed from "Uploaded Captions" to "Uploaded Files" */}
          <div className="space-y-3">
            {uploadedFiles.map((file) => ( // This line was changed from uploadedCaptions to uploadedFiles
              <div key={file.id} className="flex justify-between items-start p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                <div className="flex-1">
                  <p className="text-gray-300">{file.filename}</p> {/* This line was changed from caption.text to file.filename */}
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(file.created_at).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDeleteCaption(file.id)} // This line was changed from handleDeleteCaption(caption.id) to handleDeleteCaption(file.id)
                  className="modern-button px-3 py-1 text-sm"
                >
                  Delete
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Uploaded Images */}
      {uploadedFiles.length > 0 && ( // This line was changed from uploadedImages.length to uploadedFiles.length
        <div className="modern-card p-8">
          <h3 className="text-2xl font-bold text-white mb-6">Uploaded Files</h3> {/* This line was changed from "Uploaded Images" to "Uploaded Files" */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {uploadedFiles.map((file) => ( // This line was changed from uploadedImages to uploadedFiles
              <div key={file.id} className="relative group">
                <img
                  src={file.url} // This line was changed from image.url to file.url
                  alt={file.filename}
                  className="w-full h-48 object-cover rounded-lg border border-gray-700"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all duration-200 flex items-center justify-center rounded-lg">
                  <button
                    onClick={() => handleDeleteImage(file.id, file.filename)} // This line was changed from handleDeleteImage(image.id, image.filename) to handleDeleteImage(file.id, file.filename)
                    className="modern-button px-3 py-1 text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
} 