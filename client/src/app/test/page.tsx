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
      .then(response => response.json())
      .then(data => {
        setBackendStatus('connected');
        setApiTest(JSON.stringify(data, null, 2));
      })
      .catch(error => {
        setBackendStatus('error');
        setApiTest(`Error: ${error.message}`);
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Backend Connection Test
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Backend Status */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Backend Status
            </h2>
            
            <div className="space-y-4">
              <div>
                <span className="text-sm font-medium text-gray-500">Backend URL:</span>
                <span className="ml-2 text-sm text-gray-900">{backendUrl}</span>
              </div>
              
              <div>
                <span className="text-sm font-medium text-gray-500">Status:</span>
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
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              API Response
            </h2>
            
            <div className="bg-gray-50 p-4 rounded-md">
              <pre className="text-xs text-gray-800 overflow-auto">
                {apiTest}
              </pre>
            </div>
          </div>
        </div>

        {/* Test Links */}
        <div className="mt-8 bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Test Links
          </h2>
          
          <div className="space-y-2">
            <a 
              href={`${backendUrl}/`}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-blue-600 hover:text-blue-800"
            >
              Backend Root: {backendUrl}/
            </a>
            
            <a 
              href={`${backendUrl}/api/status`}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-blue-600 hover:text-blue-800"
            >
              Backend Status: {backendUrl}/api/status
            </a>
            
            <a 
              href={`${backendUrl}/api/health`}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-blue-600 hover:text-blue-800"
            >
              Backend Health: {backendUrl}/api/health
            </a>
          </div>
        </div>
      </div>
    </div>
  );
} 