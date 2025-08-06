'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { DashboardLayout } from '@/components/dashboard/Layout';
import { fetchCaptions, fetchImages, type Caption, type Image } from '@/lib/api/services';
import { Upload, FileText, Image as ImageIcon, Plus, Trash2 } from 'lucide-react';

export default function UploadPage() {
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [images, setImages] = useState<Image[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'captions' | 'images'>('captions');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [captionsData, imagesData] = await Promise.all([
        fetchCaptions(),
        fetchImages(),
      ]);
      
      setCaptions(captionsData || []);
      setImages(imagesData || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCaption = async (id: string) => {
    try {
      // For now, just reload captions after deleting
      const data = await fetchCaptions();
      setCaptions(data || []);
    } catch (error) {
      console.error('Failed to delete caption:', error);
    }
  };

  const handleDeleteImage = async (id: string) => {
    try {
      // For now, just reload images after deleting
      const data = await fetchImages();
      setImages(data || []);
    } catch (error) {
      console.error('Failed to delete image:', error);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Upload</h1>
          <p className="text-gray-600 mt-2">
            Manage your captions and images for posting
          </p>
        </div>

        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('captions')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'captions'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <FileText className="inline mr-2 h-4 w-4" />
                Captions ({captions.length})
              </button>
              <button
                onClick={() => setActiveTab('images')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'images'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <ImageIcon className="inline mr-2 h-4 w-4" />
                Images ({images.length})
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'captions' ? (
          <CaptionsTab 
            captions={captions} 
            onAdd={(caption) => setCaptions([...captions, caption])}
            onDelete={handleDeleteCaption}
          />
        ) : (
          <ImagesTab 
            images={images}
            onAdd={(image) => setImages([...images, image])}
            onDelete={handleDeleteImage}
          />
        )}
      </div>
    </DashboardLayout>
  );
}

interface CaptionsTabProps {
  captions: Caption[];
  onAdd: (caption: Caption) => void;
  onDelete: (id: string) => void;
}

function CaptionsTab({ captions, onAdd, onDelete }: CaptionsTabProps) {
  const [showForm, setShowForm] = useState(false);
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // For now, just reload captions after creating
      const data = await fetchCaptions();
      if (data) {
        onAdd(data[data.length - 1]); // Add the last item
      }
      setText('');
      setShowForm(false);
    } catch (error) {
      console.error('Failed to create caption:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Add Caption Form */}
      {showForm && (
        <Card>
          <CardHeader>
            <CardTitle>Add New Caption</CardTitle>
            <CardDescription>
              Create a new caption for your posts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="caption">Caption Text</Label>
                <Textarea
                  id="caption"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Enter your caption text..."
                  rows={4}
                  required
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Caption'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Captions List */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Captions</CardTitle>
            <CardDescription>
              Manage your caption library
            </CardDescription>
          </div>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Caption
          </Button>
        </CardHeader>
        <CardContent>
          {captions.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No captions</h3>
              <p className="mt-1 text-sm text-gray-500">
                Create your first caption to get started.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {captions.map((caption) => (
                <div
                  key={caption.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex-1">
                    <p className="text-gray-900">{caption.text}</p>
                    <div className="flex items-center space-x-4 mt-2">
                      <Badge variant="secondary">
                        Used {caption.used_count} times
                      </Badge>
                      <span className="text-sm text-gray-500">
                        Created {new Date(caption.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => onDelete(caption.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface ImagesTabProps {
  images: Image[];
  onAdd: (image: Image) => void;
  onDelete: (id: string) => void;
}

function ImagesTab({ images, onAdd, onDelete }: ImagesTabProps) {
  const [uploading, setUploading] = useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      // For now, just reload images after uploading
      const data = await fetchImages();
      if (data) {
        onAdd(data[data.length - 1]); // Add the last item
      }
    } catch (error) {
      console.error('Failed to upload image:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Image */}
      <Card>
        <CardHeader>
          <CardTitle>Upload Image</CardTitle>
          <CardDescription>
            Upload images to use in your posts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="image">Select Image</Label>
              <Input
                id="image"
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                disabled={uploading}
              />
            </div>
            {uploading && (
              <div className="text-sm text-gray-600">
                Uploading image...
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Images List */}
      <Card>
        <CardHeader>
          <CardTitle>Images</CardTitle>
          <CardDescription>
            Manage your image library
          </CardDescription>
        </CardHeader>
        <CardContent>
          {images.length === 0 ? (
            <div className="text-center py-8">
              <ImageIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No images</h3>
              <p className="mt-1 text-sm text-gray-500">
                Upload your first image to get started.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {images.map((image) => (
                <div
                  key={image.id}
                  className="border rounded-lg overflow-hidden"
                >
                  <div className="aspect-square bg-gray-100">
                    <img
                      src={image.url}
                      alt={image.filename}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="p-4">
                    <h3 className="font-medium text-gray-900 truncate">
                      {image.filename}
                    </h3>
                    <div className="flex items-center justify-between mt-2">
                      <Badge variant="secondary">
                        Used {image.used_count} times
                      </Badge>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onDelete(image.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 