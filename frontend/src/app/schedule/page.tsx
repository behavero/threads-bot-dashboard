'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { DashboardLayout } from '@/components/dashboard/Layout';
import { fetchSchedule, fetchAccounts, fetchCaptions, fetchImages, type Schedule, type Account, type Caption, type Image } from '@/lib/api/services';
import { Clock, Plus, Calendar } from 'lucide-react';

export default function SchedulePage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [images, setImages] = useState<Image[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [schedulesData, accountsData, captionsData, imagesData] = await Promise.all([
        fetchSchedule(),
        fetchAccounts(),
        fetchCaptions(),
        fetchImages(),
      ]);
      
      setSchedules(schedulesData || []);
      setAccounts(accountsData || []);
      setCaptions(captionsData || []);
      setImages(imagesData || []);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: Schedule['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'posted':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
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
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Schedule</h1>
            <p className="text-gray-600 mt-2">
              Configure when your accounts should post content
            </p>
          </div>
          <Button onClick={() => setShowForm(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Schedule
          </Button>
        </div>

        {/* Schedule Form */}
        {showForm && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Create New Schedule</CardTitle>
              <CardDescription>
                Set up a new posting schedule for your accounts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ScheduleForm 
                accounts={accounts}
                captions={captions}
                images={images}
                onCancel={() => setShowForm(false)}
                onSuccess={() => {
                  setShowForm(false);
                  loadData();
                }}
              />
            </CardContent>
          </Card>
        )}

        {/* Schedules List */}
        <Card>
          <CardHeader>
            <CardTitle>Scheduled Posts</CardTitle>
            <CardDescription>
              View and manage your scheduled posts
            </CardDescription>
          </CardHeader>
          <CardContent>
            {schedules.length === 0 ? (
              <div className="text-center py-8">
                <Clock className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No scheduled posts</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Create your first scheduled post to get started.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {schedules.map((schedule) => {
                  const account = accounts.find(a => a.id === schedule.account_id);
                  const caption = captions.find(c => c.id === schedule.caption_id);
                  const image = images.find(i => i.id === schedule.image_id);

                  return (
                    <div
                      key={schedule.id}
                      className="flex items-center justify-between p-4 border rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <Calendar className="h-5 w-5 text-gray-400" />
                        <div>
                          <h3 className="font-medium text-gray-900">
                            {account?.username || 'Unknown Account'}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {formatDateTime(schedule.scheduled_time)}
                          </p>
                          {caption && (
                            <p className="text-sm text-gray-500">
                              Caption: {caption.text.substring(0, 50)}...
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getStatusColor(schedule.status)}>
                          {schedule.status}
                        </Badge>
                        <Button variant="outline" size="sm">
                          Edit
                        </Button>
                        <Button variant="outline" size="sm">
                          Delete
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

interface ScheduleFormProps {
  accounts: Account[];
  captions: Caption[];
  images: Image[];
  onCancel: () => void;
  onSuccess: () => void;
}

function ScheduleForm({ accounts, captions, images, onCancel, onSuccess }: ScheduleFormProps) {
  const [formData, setFormData] = useState({
    account_id: '',
    caption_id: '',
    image_id: '',
    scheduled_time: '',
    status: 'pending' as const,
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      // For now, just call onSuccess
      onSuccess();
    } catch (error) {
      console.error('Failed to create schedule:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="account">Account</Label>
          <Select value={formData.account_id} onValueChange={(value) => setFormData({ ...formData, account_id: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select account" />
            </SelectTrigger>
            <SelectContent>
              {accounts.map((account) => (
                <SelectItem key={account.id} value={account.id}>
                  @{account.username}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="scheduled_time">Scheduled Time</Label>
          <Input
            type="datetime-local"
            value={formData.scheduled_time}
            onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="caption">Caption (Optional)</Label>
          <Select value={formData.caption_id} onValueChange={(value) => setFormData({ ...formData, caption_id: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select caption" />
            </SelectTrigger>
            <SelectContent>
              {captions.map((caption) => (
                <SelectItem key={caption.id} value={caption.id}>
                  {caption.text.substring(0, 30)}...
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="image">Image (Optional)</Label>
          <Select value={formData.image_id} onValueChange={(value) => setFormData({ ...formData, image_id: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select image" />
            </SelectTrigger>
            <SelectContent>
              {images.map((image) => (
                <SelectItem key={image.id} value={image.id}>
                  {image.filename}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={loading}>
          {loading ? 'Creating...' : 'Create Schedule'}
        </Button>
      </div>
    </form>
  );
} 