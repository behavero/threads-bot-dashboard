'use client';

import { useState, useEffect } from 'react';

export default function Dashboard() {
  const [status, setStatus] = useState('loading');
  const [backendUrl, setBackendUrl] = useState('');

  useEffect(() => {
    // Get backend URL from environment
    const url = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000';
    setBackendUrl(url);
    
    // Check backend status
    fetch(`${url}/api/status`)
      .then(response => response.json())
      .then(data => {
        setStatus(data.status || 'unknown');
      })
      .catch(error => {
        console.error('Error checking backend status:', error);
        setStatus('error');
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            Threads Bot Dashboard
          </h1>
          
          <div className="bg-white shadow rounded-lg p-6 max-w-md mx-auto">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Backend Status
            </h2>
            
            <div className="space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-500">Status:</span>
                <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
                  status === 'running' ? 'bg-green-100 text-green-800' :
                  status === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {status}
                </span>
              </div>
              
              <div>
                <span className="text-sm font-medium text-gray-500">Backend URL:</span>
                <span className="ml-2 text-sm text-gray-900">{backendUrl}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 