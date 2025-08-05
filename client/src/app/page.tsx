'use client';

import { useState, useEffect } from 'react';
import { 
  PlusIcon, 
  UserIcon, 
  DocumentTextIcon, 
  PhotoIcon, 
  PlayIcon,
  StopIcon,
  TrashIcon,
  ChartBarIcon,
  CogIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface Account {
  id: string;
  username: string;
  active: boolean;
  last_posted?: string;
  posts_count?: number;
  shadowban?: boolean;
}

interface Caption {
  id: string;
  text: string;
  used: boolean;
  created_at: string;
}

interface Image {
  id: string;
  url: string;
  used: boolean;
  created_at: string;
}

interface PostingHistory {
  id: string;
  account_id: string;
  status: string;
  error_message?: string;
  posted_at?: string;
  created_at: string;
}

export default function Dashboard() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [captions, setCaptions] = useState<Caption[]>([]);
  const [images, setImages] = useState<Image[]>([]);
  const [postingHistory, setPostingHistory] = useState<PostingHistory[]>([]);
  const [botStatus, setBotStatus] = useState('loading');
  const [loading, setLoading] = useState(true);
  const [backendUrl, setBackendUrl] = useState('');
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [activeTab, setActiveTab] = useState('overview');

  const [newAccount, setNewAccount] = useState({ username: '', password: '' });
  const [newCaption, setNewCaption] = useState('');
  const [newImage, setNewImage] = useState('');

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://threads-bot-dashboard-3.onrender.com';
    setBackendUrl(url);
    fetchData(url);
    const interval = setInterval(() => fetchData(url), 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async (url: string) => {
    try {
      console.log('Fetching data from:', url);
      setConnectionStatus('connecting');
      
      // Test connection first
      const healthResponse = await fetch(`${url}/api/health`);
      if (!healthResponse.ok) {
        throw new Error(`Health check failed: ${healthResponse.status}`);
      }
      setConnectionStatus('connected');
      
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

      // Fetch captions and images (mock data for now)
      setCaptions([
        { id: '1', text: 'Amazing day! 🌟', used: false, created_at: '2025-08-05T19:00:00Z' },
        { id: '2', text: 'Life is beautiful ✨', used: true, created_at: '2025-08-05T18:00:00Z' },
        { id: '3', text: 'Living the dream 💫', used: false, created_at: '2025-08-05T17:00:00Z' }
      ]);
      
      setImages([
        { id: '1', url: 'https://picsum.photos/400/300?random=1', used: false, created_at: '2025-08-05T19:00:00Z' },
        { id: '2', url: 'https://picsum.photos/400/300?random=2', used: true, created_at: '2025-08-05T18:00:00Z' },
        { id: '3', url: 'https://picsum.photos/400/300?random=3', used: false, created_at: '2025-08-05T17:00:00Z' }
      ]);

      // Mock posting history
      setPostingHistory([
        { id: '1', account_id: '1', status: 'success', posted_at: '2025-08-05T19:30:00Z', created_at: '2025-08-05T19:30:00Z' },
        { id: '2', account_id: '1', status: 'error', error_message: 'Rate limited', created_at: '2025-08-05T19:00:00Z' },
        { id: '3', account_id: '2', status: 'success', posted_at: '2025-08-05T18:30:00Z', created_at: '2025-08-05T18:30:00Z' }
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
      setBotStatus('error');
      setConnectionStatus('error');
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

  const toggleAccountStatus = async (accountId: string, currentStatus: boolean) => {
    try {
      const response = await fetch(`${backendUrl}/api/accounts/${accountId}/toggle`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ active: !currentStatus }),
      });

      if (response.ok) {
        toast.success(`Account ${currentStatus ? 'deactivated' : 'activated'} successfully`);
        fetchData(backendUrl);
      } else {
        toast.error('Failed to update account status');
      }
    } catch (error) {
      toast.error('Error updating account status');
    }
  };

  const deleteAccount = async (accountId: string) => {
    if (!confirm('Are you sure you want to delete this account?')) return;

    try {
      const response = await fetch(`${backendUrl}/api/accounts/${accountId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        toast.success('Account deleted successfully');
        fetchData(backendUrl);
      } else {
        toast.error('Failed to delete account');
      }
    } catch (error) {
      toast.error('Error deleting account');
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

  const getAccountStats = (accountId: string) => {
    const accountHistory = postingHistory.filter(h => h.account_id === accountId);
    const successful = accountHistory.filter(h => h.status === 'success').length;
    const failed = accountHistory.filter(h => h.status === 'error').length;
    const total = accountHistory.length;
    
    return { successful, failed, total };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-yellow-400 mx-auto"></div>
          <p className="mt-4 text-gray-300">Loading dashboard...</p>
          <p className="text-sm text-gray-500 mt-2">Backend: {backendUrl}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-white">Threads Bot Dashboard</h1>
              <p className="text-gray-400">Auto-posting bot for Threads</p>
              <div className="flex items-center space-x-4 mt-2">
                <span className="text-sm text-gray-500">Backend: {backendUrl}</span>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  connectionStatus === 'connected' ? 'bg-green-100 text-green-800' :
                  connectionStatus === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {connectionStatus}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-2 ${
                  botStatus === 'running' ? 'bg-green-500' : 'bg-red-500'
                }`}></div>
                <span className="text-sm text-gray-300">
                  Bot: {botStatus === 'running' ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {[
              { id: 'overview', name: 'Overview', icon: ChartBarIcon },
              { id: 'accounts', name: 'Accounts', icon: UserIcon },
              { id: 'content', name: 'Content', icon: DocumentTextIcon },
              { id: 'history', name: 'History', icon: ClockIcon },
              { id: 'settings', name: 'Settings', icon: CogIcon }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-yellow-400 text-yellow-400'
                    : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="card">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <UserIcon className="h-8 w-8 text-yellow-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Total Accounts</p>
                    <p className="text-2xl font-bold text-white">{accounts.length}</p>
                  </div>
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <DocumentTextIcon className="h-8 w-8 text-yellow-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Available Captions</p>
                    <p className="text-2xl font-bold text-white">{captions.filter(c => !c.used).length}</p>
                  </div>
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <PhotoIcon className="h-8 w-8 text-yellow-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Available Images</p>
                    <p className="text-2xl font-bold text-white">{images.filter(i => !i.used).length}</p>
                  </div>
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <ChartBarIcon className="h-8 w-8 text-yellow-400" />
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-400">Total Posts</p>
                    <p className="text-2xl font-bold text-white">{postingHistory.filter(h => h.status === 'success').length}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {postingHistory.slice(0, 5).map((post) => {
                  const account = accounts.find(a => a.id === post.account_id);
                  return (
                    <div key={post.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          post.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                        }`}></div>
                        <span className="text-sm text-gray-300">
                          {account?.username || 'Unknown'} - {post.status}
                        </span>
                      </div>
                      <span className="text-xs text-gray-400">
                        {new Date(post.created_at).toLocaleString()}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Accounts Tab */}
        {activeTab === 'accounts' && (
          <div className="space-y-6">
            {/* Add Account Form */}
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">Add New Account</h3>
              <form onSubmit={addAccount} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <input
                    type="text"
                    placeholder="Username"
                    value={newAccount.username}
                    onChange={(e) => setNewAccount({ ...newAccount, username: e.target.value })}
                    className="input-field"
                  />
                  <input
                    type="password"
                    placeholder="Password"
                    value={newAccount.password}
                    onChange={(e) => setNewAccount({ ...newAccount, password: e.target.value })}
                    className="input-field"
                  />
                </div>
                <button type="submit" className="btn-primary">
                  <PlusIcon className="w-5 h-5 mr-2" />
                  Add Account
                </button>
              </form>
            </div>

            {/* Accounts List */}
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">Manage Accounts</h3>
              <div className="space-y-4">
                {accounts.map((account) => {
                  const stats = getAccountStats(account.id);
                  return (
                    <div key={account.id} className="bg-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="flex-shrink-0">
                            <UserIcon className="h-8 w-8 text-yellow-400" />
                          </div>
                          <div>
                            <h4 className="text-white font-medium">{account.username}</h4>
                            <div className="flex items-center space-x-4 mt-1">
                              <span className={`status-badge ${
                                account.active ? 'status-active' : 'status-inactive'
                              }`}>
                                {account.active ? 'Active' : 'Inactive'}
                              </span>
                              {account.shadowban && (
                                <span className="status-badge bg-red-100 text-red-800">
                                  Shadowbanned
                                </span>
                              )}
                            </div>
                            <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400">
                              <span>Posts: {stats.successful}/{stats.total}</span>
                              <span>Success Rate: {stats.total > 0 ? Math.round((stats.successful / stats.total) * 100) : 0}%</span>
                              {account.last_posted && (
                                <span>Last: {new Date(account.last_posted).toLocaleString()}</span>
                              )}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => toggleAccountStatus(account.id, account.active)}
                            className={`btn-secondary ${account.active ? 'text-red-400' : 'text-green-400'}`}
                          >
                            {account.active ? <StopIcon className="w-4 h-4" /> : <PlayIcon className="w-4 h-4" />}
                          </button>
                          <button
                            onClick={() => deleteAccount(account.id)}
                            className="btn-danger"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Content Tab */}
        {activeTab === 'content' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Captions */}
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">Manage Captions</h3>
              <form onSubmit={addCaption} className="mb-4">
                <textarea
                  placeholder="Enter caption text..."
                  value={newCaption}
                  onChange={(e) => setNewCaption(e.target.value)}
                  rows={3}
                  className="input-field w-full"
                />
                <button type="submit" className="btn-primary mt-2">
                  <PlusIcon className="w-4 h-4 mr-2" />
                  Add Caption
                </button>
              </form>
              <div className="space-y-2">
                {captions.map((caption) => (
                  <div key={caption.id} className="p-3 bg-gray-700 rounded-lg">
                    <p className="text-sm text-gray-300">{caption.text}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className={`status-badge ${
                        caption.used ? 'status-inactive' : 'status-active'
                      }`}>
                        {caption.used ? 'Used' : 'Available'}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(caption.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Images */}
            <div className="card">
              <h3 className="text-lg font-semibold text-white mb-4">Manage Images</h3>
              <form onSubmit={addImage} className="mb-4">
                <input
                  type="url"
                  placeholder="Image URL"
                  value={newImage}
                  onChange={(e) => setNewImage(e.target.value)}
                  className="input-field w-full"
                />
                <button type="submit" className="btn-primary mt-2">
                  <PlusIcon className="w-4 h-4 mr-2" />
                  Add Image
                </button>
              </form>
              <div className="space-y-2">
                {images.map((image) => (
                  <div key={image.id} className="p-3 bg-gray-700 rounded-lg">
                    <img src={image.url} alt="Post image" className="w-full h-24 object-cover rounded-md mb-2" />
                    <div className="flex items-center justify-between">
                      <span className={`status-badge ${
                        image.used ? 'status-inactive' : 'status-active'
                      }`}>
                        {image.used ? 'Used' : 'Available'}
                      </span>
                      <span className="text-xs text-gray-400">
                        {new Date(image.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Posting History</h3>
            <div className="space-y-3">
              {postingHistory.map((post) => {
                const account = accounts.find(a => a.id === post.account_id);
                return (
                  <div key={post.id} className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`w-3 h-3 rounded-full ${
                        post.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                      }`}></div>
                      <div>
                        <p className="text-white font-medium">{account?.username || 'Unknown Account'}</p>
                        <p className="text-sm text-gray-400">
                          Status: {post.status} {post.error_message && `- ${post.error_message}`}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-400">
                        {post.posted_at ? new Date(post.posted_at).toLocaleString() : 'Pending'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {new Date(post.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Settings Tab */}
        {activeTab === 'settings' && (
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Bot Settings</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <div>
                  <h4 className="text-white font-medium">Bot Status</h4>
                  <p className="text-sm text-gray-400">Control the main bot process</p>
                </div>
                <button className="btn-primary">
                  {botStatus === 'running' ? 'Stop Bot' : 'Start Bot'}
                </button>
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <div>
                  <h4 className="text-white font-medium">Posting Interval</h4>
                  <p className="text-sm text-gray-400">Time between posts (minutes)</p>
                </div>
                <input
                  type="number"
                  defaultValue="5"
                  className="input-field w-20 text-center"
                />
              </div>
              
              <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
                <div>
                  <h4 className="text-white font-medium">Error Notifications</h4>
                  <p className="text-sm text-gray-400">Get notified of posting errors</p>
                </div>
                <button className="btn-secondary">Configure</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 