'use client';

import { useState, useEffect } from 'react';
import { PlusIcon, UserIcon, DocumentTextIcon, PhotoIcon, ClockIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface Account {
  id: string;
  username: string;
  active: boolean;
  last_posted?: string;
}

interface Caption {
  id: string;
  text: string;
  used: boolean;
}

interface Image {
  id: string;
  url: string;
  used: boolean;
}

export default function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [images, setImages] = useState<Image[]>([]);
  const [botStatus, setBotStatus] = useState('loading');
  const [loading, setLoading] = useState(true);
  const [backendUrl, setBackendUrl] = useState('');

  const [newAccount, setNewAccount] = useState({ username: '', password: '' });
  const [newCaption, setNewCaption] = useState('');
  const [newImage, setNewImage] = useState('');

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://threads-bot-dashboard-3.onrender.com';
    setBackendUrl(url);
    fetchData(url);
    const interval = setInterval(() => fetchData(url), 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async (url: string) => {
    try {
      console.log('Fetching data from:', url);
      
      // Fetch bot status
      const statusResponse = await fetch(`${url}/api/status`);
      if (!statusResponse.ok) {
        throw new Error(`Status API returned ${statusResponse.status}`);
      }
      const statusData = await statusResponse.json();
      setBotStatus(statusData.status);

      // Fetch accounts
      const accountsResponse = await fetch(`${url}/api/accounts`);
      if (accountsResponse.ok) {
        const accountsData = await accountsResponse.json();
        setAccounts(accountsData.accounts || []);
      } else {
        console.warn('Accounts API returned:', accountsResponse.status);
        setAccounts([]);
      }

      // Fetch captions and images (these endpoints need to be implemented)
      // For now, we'll use empty arrays
      setCaptions([]);
      setImages([]);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setBotStatus('error');
      setLoading(false);
      toast.error('Failed to connect to backend');
    }
  };

  const addAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAccount.username || !newAccount.password) {
      toast.error('Username and password are required');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/accounts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newAccount),
      });

      if (response.ok) {
        toast.success('Account added successfully');
        setNewAccount({ username: '', password: '' });
        fetchData(backendUrl);
      } else {
        const errorData = await response.json();
        toast.error(`Failed to add account: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      toast.error('Error adding account');
    }
  };

  const addCaption = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCaption.trim()) {
      toast.error('Caption text is required');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/captions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: newCaption }),
      });

      if (response.ok) {
        toast.success('Caption added successfully');
        setNewCaption('');
        fetchData(backendUrl);
      } else {
        const errorData = await response.json();
        toast.error(`Failed to add caption: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      toast.error('Error adding caption');
    }
  };

  const addImage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newImage.trim()) {
      toast.error('Image URL is required');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/images`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: newImage }),
      });

      if (response.ok) {
        toast.success('Image added successfully');
        setNewImage('');
        fetchData(backendUrl);
      } else {
        const errorData = await response.json();
        toast.error(`Failed to add image: ${errorData.error || 'Unknown error'}`);
      }
    } catch (error) {
      toast.error('Error adding image');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            Threads Bot Dashboard
          </h1>
          
          <div className="bg-white shadow rounded-lg p-6 max-w-md mx-auto">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
            <p className="text-sm text-gray-500 mt-2">Backend: {backendUrl}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Threads Bot Dashboard</h1>
              <p className="text-gray-600">Auto-posting bot for Threads</p>
              <p className="text-sm text-gray-500">Backend: {backendUrl}</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  botStatus === 'running' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm text-gray-600">
                  Bot: {botStatus === 'running' ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Accounts Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <UserIcon className="w-5 h-5 mr-2" />
                Accounts ({accounts.length})
              </h2>
            </div>

            {/* Add Account Form */}
            <form onSubmit={addAccount} className="mb-4 space-y-3">
              <input
                type="text"
                placeholder="Username"
                value={newAccount.username}
                onChange={(e) => setNewAccount({ ...newAccount, username: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <input
                type="password"
                placeholder="Password"
                value={newAccount.password}
                onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                type="submit"
                className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                Add Account
              </button>
            </form>

            {/* Accounts List */}
            <div className="space-y-2">
              {accounts.map((account) => (
                <div key={account.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div>
                    <p className="font-medium text-gray-900">{account.username}</p>
                    <p className="text-sm text-gray-500">
                      {account.last_posted ? `Last posted: ${new Date(account.last_posted).toLocaleString()}` : 'Never posted'}
                    </p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs ${
                    account.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {account.active ? 'Active' : 'Inactive'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Captions Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <DocumentTextIcon className="w-5 h-5 mr-2" />
                Captions ({captions.length})
              </h2>
            </div>

            {/* Add Caption Form */}
            <form onSubmit={addCaption} className="mb-4">
              <textarea
                placeholder="Enter caption text..."
                value={newCaption}
                onChange={(e) => setNewCaption(e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                type="submit"
                className="w-full mt-2 bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                Add Caption
              </button>
            </form>

            {/* Captions List */}
            <div className="space-y-2">
              {captions.map((caption) => (
                <div key={caption.id} className="p-3 bg-gray-50 rounded-md">
                  <p className="text-sm text-gray-900">{caption.text}</p>
                  <div className={`inline-block mt-1 px-2 py-1 rounded-full text-xs ${
                    caption.used ? 'bg-gray-100 text-gray-600' : 'bg-green-100 text-green-800'
                  }`}>
                    {caption.used ? 'Used' : 'Available'}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Images Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                <PhotoIcon className="w-5 h-5 mr-2" />
                Images ({images.length})
              </h2>
            </div>

            {/* Add Image Form */}
            <form onSubmit={addImage} className="mb-4 space-y-3">
              <input
                type="url"
                placeholder="Image URL"
                value={newImage}
                onChange={(e) => setNewImage(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                type="submit"
                className="w-full bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                Add Image
              </button>
            </form>

            {/* Images List */}
            <div className="space-y-2">
              {images.map((image) => (
                <div key={image.id} className="p-3 bg-gray-50 rounded-md">
                  <img src={image.url} alt="Post image" className="w-full h-24 object-cover rounded-md mb-2" />
                  <div className={`inline-block px-2 py-1 rounded-full text-xs ${
                    image.used ? 'bg-gray-100 text-gray-600' : 'bg-green-100 text-green-800'
                  }`}>
                    {image.used ? 'Used' : 'Available'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 