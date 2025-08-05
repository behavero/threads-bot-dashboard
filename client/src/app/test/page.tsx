'use client';

import { useState, useEffect } from 'react';

export default function TestPage() {
  const [backendStatus, setBackendStatus] = useState('loading');
  const [backendUrl, setBackendUrl] = useState('');
  const [apiTest, setApiTest] = useState('');

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://threads-bot-dashboard-3.onrender.com';
    setBackendUrl(url);
    
    // Test backend connectivity
    fetch(`${url}/api/status`)
      .then(response => {
        console.log('Response status:', response.status);
        return response.json();
      })
      .then(data => {
        console.log('Response data:', data);
        setBackendStatus('connected');
        setApiTest(JSON.stringify(data, null, 2));
      })
      .catch(error => {
        console.error('Fetch error:', error);
        setBackendStatus('error');
        setApiTest(`Error: ${error.message}`);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Backend Connection Test</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Backend Status */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Backend Status</h2>
            
            <div className="space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-400">Backend URL:</span>
                <span className="ml-2 text-sm text-gray-300">{backendUrl}</span>
              </div>
              
              <div>
                <span className="text-sm font-medium text-gray-400">Status:</span>
                <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${
                  backendStatus === 'connected' ? 'bg-green-100 text-green-800' :
                  backendStatus === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {backendStatus}
                </span>
              </div>
            </div>
          </div>

          {/* API Test */}
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">API Response</h2>
            
            <div className="bg-gray-700 p-4 rounded-md">
              <pre className="text-xs text-gray-300 overflow-auto">
                {apiTest}
              </pre>
            </div>
          </div>
        </div>

        {/* Test Links */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Test Links</h2>
          
          <div className="space-y-2">
            <a 
              href={`${backendUrl}/`}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-yellow-400 hover:text-yellow-300"
            >
              Backend Root: {backendUrl}/
            </a>
            
            <a 
              href={`${backendUrl}/api/status`}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-yellow-400 hover:text-yellow-300"
            >
              Backend Status: {backendUrl}/api/status
            </a>
            
            <a 
              href={`${backendUrl}/api/health`}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-yellow-400 hover:text-yellow-300"
            >
              Backend Health: {backendUrl}/api/health
            </a>
          </div>
        </div>

        {/* Environment Variables */}
        <div className="mt-8 bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Environment Variables</h2>
          
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-400">NEXT_PUBLIC_BACKEND_URL:</span>
              <span className="ml-2 text-gray-300">{process.env.NEXT_PUBLIC_BACKEND_URL || 'NOT SET'}</span>
            </div>
            <div>
              <span className="text-gray-400">NEXT_PUBLIC_SUPABASE_URL:</span>
              <span className="ml-2 text-gray-300">{process.env.NEXT_PUBLIC_SUPABASE_URL || 'NOT SET'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 