'use client'

import { useState, useEffect } from 'react'

interface Caption {
  id: number
  text: string
  category: string
  tags: string[]
  used: boolean
  created_at: string
  updated_at: string
}

export default function CaptionsPage() {
  const [captions, setCaptions] = useState<Caption[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [newCaption, setNewCaption] = useState({
    text: '',
    category: 'general',
    tags: [] as string[]
  })
  const [tagInput, setTagInput] = useState('')
  const [uploading, setUploading] = useState(false)
  const [csvFile, setCsvFile] = useState<File | null>(null)

  // Fetch captions from backend directly
  const fetchCaptions = async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Call backend directly instead of frontend API
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/captions')
      
      if (response.ok) {
        const data = await response.json()
        setCaptions(data.captions || [])
      } else {
        throw new Error(`Failed to fetch captions: ${response.status}`)
      }
    } catch (err) {
      console.error('Error fetching captions:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch captions')
    } finally {
      setLoading(false)
    }
  }

  // Add caption using backend directly
  const addCaption = async () => {
    if (!newCaption.text.trim()) {
      setError('Caption text is required')
      return
    }

    try {
      setUploading(true)
      setError(null)

      // Call backend directly
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/captions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          text: newCaption.text,
          category: newCaption.category,
          tags: newCaption.tags
        })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('Caption added successfully:', data)
        
        // Reset form
        setNewCaption({
          text: '',
          category: 'general',
          tags: []
        })
        setTagInput('')
        
        // Refresh captions
        await fetchCaptions()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to add caption')
      }
    } catch (err) {
      console.error('Error adding caption:', err)
      setError(err instanceof Error ? err.message : 'Failed to add caption')
    } finally {
      setUploading(false)
    }
  }

  // Upload CSV using backend directly
  const uploadCSV = async () => {
    if (!csvFile) {
      setError('Please select a CSV file')
      return
    }

    try {
      setUploading(true)
      setError(null)

      const formData = new FormData()
      formData.append('file', csvFile)

      // Call backend directly for CSV upload
      const response = await fetch('https://threads-bot-dashboard-3.onrender.com/api/captions/upload-csv', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data = await response.json()
        console.log('CSV uploaded successfully:', data)
        
        // Reset file input
        setCsvFile(null)
        
        // Refresh captions
        await fetchCaptions()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to upload CSV')
      }
    } catch (err) {
      console.error('Error uploading CSV:', err)
      setError(err instanceof Error ? err.message : 'Failed to upload CSV')
    } finally {
      setUploading(false)
    }
  }

  // Add tag to new caption
  const addTag = () => {
    if (tagInput.trim() && !newCaption.tags.includes(tagInput.trim())) {
      setNewCaption(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }))
      setTagInput('')
    }
  }

  // Remove tag from new caption
  const removeTag = (tagToRemove: string) => {
    setNewCaption(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  useEffect(() => {
    fetchCaptions()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="modern-card p-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400 mx-auto"></div>
              <p className="mt-4 text-gray-300">Loading captions...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="modern-card p-8">
          <h1 className="text-3xl font-bold gradient-text mb-8">Captions Management</h1>
          
          {error && (
            <div className="bg-red-900/20 border border-red-500 text-red-300 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          {/* Add New Caption */}
          <div className="modern-card p-6 mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Add New Caption</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Caption Text</label>
                <textarea
                  value={newCaption.text}
                  onChange={(e) => setNewCaption(prev => ({ ...prev, text: e.target.value }))}
                  className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  rows={3}
                  placeholder="Enter your caption text..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
                <input
                  type="text"
                  value={newCaption.category}
                  onChange={(e) => setNewCaption(prev => ({ ...prev, category: e.target.value }))}
                  className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                  placeholder="general"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Tags</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                    className="flex-1 p-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
                    placeholder="Add a tag..."
                  />
                  <button
                    onClick={addTag}
                    className="modern-button px-4 py-3"
                  >
                    Add
                  </button>
                </div>
                {newCaption.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {newCaption.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-purple-600 text-white"
                      >
                        {tag}
                        <button
                          onClick={() => removeTag(tag)}
                          className="ml-2 text-purple-200 hover:text-white"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={addCaption}
                disabled={uploading || !newCaption.text.trim()}
                className="modern-button w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Adding...' : 'Add Caption'}
              </button>
            </div>
          </div>

          {/* CSV Upload */}
          <div className="modern-card p-6 mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Upload CSV</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">CSV File</label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                  className="w-full p-3 bg-gray-800 border border-gray-600 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-purple-600 file:text-white hover:file:bg-purple-700"
                />
              </div>

              <div className="text-sm text-gray-400">
                <p>CSV format: text,category,tags</p>
                <p>Example: "Hello world",general,"tag1|tag2|tag3"</p>
              </div>

              <button
                onClick={uploadCSV}
                disabled={uploading || !csvFile}
                className="modern-button w-full py-3 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Uploading...' : 'Upload CSV'}
              </button>
            </div>
          </div>

          {/* Captions List */}
          <div className="modern-card p-6">
            <h2 className="text-xl font-semibold text-white mb-4">All Captions ({captions.length})</h2>
            
            {captions.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No captions found. Add your first caption above!</p>
            ) : (
              <div className="space-y-4">
                {captions.map((caption) => (
                  <div key={caption.id} className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <p className="text-white font-medium">{caption.text}</p>
                      <span className={`px-2 py-1 rounded text-xs ${
                        caption.used ? 'bg-green-600 text-green-100' : 'bg-yellow-600 text-yellow-100'
                      }`}>
                        {caption.used ? 'Used' : 'Available'}
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                      <span>Category: {caption.category}</span>
                      <span>Created: {new Date(caption.created_at).toLocaleDateString()}</span>
                    </div>
                    
                    {caption.tags && caption.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {caption.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-600 text-white"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

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