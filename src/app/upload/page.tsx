'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface Caption {
  id: number
  text: string
  created_at: string
}

interface Image {
  id: number
  filename: string
  url: string
  size: number
  type: string
  created_at: string
}

export default function UploadPage() {
  const [captions, setCaptions] = useState('')
  const [images, setImages] = useState<File[]>([])
  const [uploadedCaptions, setUploadedCaptions] = useState<Caption[]>([])
  const [uploadedImages, setUploadedImages] = useState<Image[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [supabaseStatus, setSupabaseStatus] = useState<string>('')

  useEffect(() => {
    fetchUploadedContent()
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

  const fetchUploadedContent = async () => {
    try {
      const response = await fetch('/api/upload')
      const data = await response.json()
      
      if (data.success) {
        setUploadedCaptions(data.data.captions)
        setUploadedImages(data.data.images)
      }
    } catch (error) {
      console.error('Error fetching content:', error)
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
      formData.append('captions', captions)
      
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
        setCaptions('')
        setImages([])
        // Refresh the content list
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
        setUploadedCaptions(prev => prev.filter(caption => caption.id !== id))
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
        setUploadedImages(prev => prev.filter(image => image.id !== id))
        setMessage('Image deleted successfully!')
      }
    } catch (error) {
      setMessage('Delete failed: ' + error)
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Upload Content</h1>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
          supabaseStatus === 'Connected' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-red-100 text-red-800'
        }`}>
          Supabase: {supabaseStatus || 'Checking...'}
        </div>
      </div>
      
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Upload Captions and Images</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Label htmlFor="captions">Captions (one per line)</Label>
              <Textarea
                id="captions"
                value={captions}
                onChange={(e) => setCaptions(e.target.value)}
                placeholder="Enter your captions here, one per line..."
                className="mt-2"
                rows={4}
              />
            </div>

            <div>
              <Label htmlFor="images">Images</Label>
              <Input
                id="images"
                type="file"
                multiple
                accept=".png,.jpg,.jpeg"
                onChange={handleImageChange}
                className="mt-2"
              />
              {images.length > 0 && (
                <div className="mt-2 text-sm text-gray-600">
                  Selected {images.length} file(s): {images.map(img => img.name).join(', ')}
                </div>
              )}
            </div>

            <Button type="submit" disabled={isUploading} className="w-full">
              {isUploading ? 'Uploading...' : 'Upload Content'}
            </Button>
          </form>

          {message && (
            <div className={`mt-4 p-3 rounded ${
              message.includes('successful') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {message}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Uploaded Captions */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Uploaded Captions</CardTitle>
        </CardHeader>
        <CardContent>
          {uploadedCaptions.length === 0 ? (
            <p className="text-gray-500">No captions uploaded yet.</p>
          ) : (
            <div className="space-y-3">
              {uploadedCaptions.map((caption) => (
                <div key={caption.id} className="flex justify-between items-start p-3 bg-gray-50 rounded">
                  <div className="flex-1">
                    <p className="text-sm">{caption.text}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(caption.created_at).toLocaleString()}
                    </p>
                  </div>
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => handleDeleteCaption(caption.id)}
                  >
                    Delete
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Uploaded Images */}
      <Card>
        <CardHeader>
          <CardTitle>Uploaded Images</CardTitle>
        </CardHeader>
        <CardContent>
          {uploadedImages.length === 0 ? (
            <p className="text-gray-500">No images uploaded yet.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {uploadedImages.map((image) => (
                <div key={image.id} className="border rounded-lg overflow-hidden">
                  <img
                    src={image.url}
                    alt={image.filename}
                    className="w-full h-48 object-cover"
                  />
                  <div className="p-3">
                    <p className="text-sm font-medium truncate">{image.filename}</p>
                    <p className="text-xs text-gray-500">
                      {(image.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                    <Button
                      variant="destructive"
                      size="sm"
                      className="mt-2 w-full"
                      onClick={() => handleDeleteImage(image.id, image.filename)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 