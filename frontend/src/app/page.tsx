'use client';

import { useState, useEffect } from 'react';
import { 
  UserGroupIcon, 
  ChatBubbleLeftRightIcon, 
  PhotoIcon, 
  PlayIcon, 
  StopIcon,
  CogIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface Account {
  id: string;
  username: string;
  email: string;
  enabled: boolean;
  description: string;
}

interface Caption {
  id: string;
  text: string;
}

interface Image {
  id: string;
  filename: string;
  file_path: string;
  use_count: number;
}

export default function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [images, setImages] = useState<Image[]>([]);
  const [botStatus, setBotStatus] = useState<'running' | 'stopped' | 'loading'>('loading');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    checkBotStatus();
  }, []);

  const fetchData = async () => {
    try {
      const [accountsRes, captionsRes, imagesRes] = await Promise.all([
        fetch('/api/accounts'),
        fetch('/api/captions'),
        fetch('/api/images')
      ]);

      if (accountsRes.ok) {
        const accountsData = await accountsRes.json();
        setAccounts(accountsData);
      }

      if (captionsRes.ok) {
        const captionsData = await captionsRes.json();
        setCaptions(captionsData);
      }

      if (imagesRes.ok) {
        const imagesData = await imagesRes.json();
        setImages(imagesData);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const checkBotStatus = async () => {
    try {
      const response = await fetch('/api/bot/status');
      if (response.ok) {
        const data = await response.json();
        setBotStatus(data.status);
      }
    } catch (error) {
      console.error('Error checking bot status:', error);
      setBotStatus('stopped');
    }
  };

  const startBot = async () => {
    try {
      const response = await fetch('/api/bot/start', { method: 'POST' });
      if (response.ok) {
        setBotStatus('running');
        toast.success('Bot started successfully');
      } else {
        toast.error('Failed to start bot');
      }
    } catch (error) {
      console.error('Error starting bot:', error);
      toast.error('Failed to start bot');
    }
  };

  const stopBot = async () => {
    try {
      const response = await fetch('/api/bot/stop', { method: 'POST' });
      if (response.ok) {
        setBotStatus('stopped');
        toast.success('Bot stopped successfully');
      } else {
        toast.error('Failed to stop bot');
      }
    } catch (error) {
      console.error('Error stopping bot:', error);
      toast.error('Failed to stop bot');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Enhanced Threads Bot
              </h1>
              <p className="text-gray-600">Manage your Threads automation</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  botStatus === 'running' ? 'bg-green-500' : 
                  botStatus === 'stopped' ? 'bg-red-500' : 'bg-yellow-500'
                }`}></div>
                <span className="text-sm text-gray-600 capitalize">
                  {botStatus}
                </span>
              </div>
              {botStatus === 'running' ? (
                <button
                  onClick={stopBot}
                  className="btn-secondary flex items-center space-x-2"
                >
                  <StopIcon className="w-4 h-4" />
                  <span>Stop Bot</span>
                </button>
              ) : (
                <button
                  onClick={startBot}
                  className="btn-primary flex items-center space-x-2"
                >
                  <PlayIcon className="w-4 h-4" />
                  <span>Start Bot</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <UserGroupIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Accounts</p>
                <p className="text-2xl font-semibold text-gray-900">{accounts.length}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChatBubbleLeftRightIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Captions</p>
                <p className="text-2xl font-semibold text-gray-900">{captions.length}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <PhotoIcon className="h-8 w-8 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Images</p>
                <p className="text-2xl font-semibold text-gray-900">{images.length}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <button className="card hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center">
              <UserGroupIcon className="h-6 w-6 text-primary-600" />
              <span className="ml-3 font-medium">Manage Accounts</span>
            </div>
          </button>

          <button className="card hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center">
              <ChatBubbleLeftRightIcon className="h-6 w-6 text-primary-600" />
              <span className="ml-3 font-medium">Edit Captions</span>
            </div>
          </button>

          <button className="card hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center">
              <PhotoIcon className="h-6 w-6 text-primary-600" />
              <span className="ml-3 font-medium">Upload Images</span>
            </div>
          </button>

          <button className="card hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center">
              <CogIcon className="h-6 w-6 text-primary-600" />
              <span className="ml-3 font-medium">Settings</span>
            </div>
          </button>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {accounts.slice(0, 3).map((account) => (
              <div key={account.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-b-0">
                <div>
                  <p className="font-medium text-gray-900">{account.username}</p>
                  <p className="text-sm text-gray-600">{account.description}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    account.enabled 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {account.enabled ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
} 