'use client';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-8">Threads Bot Dashboard</h1>
        <p className="text-xl text-gray-300 mb-8">Welcome to the Threads Bot Dashboard</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">✅ Success!</h2>
            <p className="text-gray-400">
              If you can see this page, the basic routing is working correctly.
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-semibold mb-4">🔧 Next Steps</h2>
            <p className="text-gray-400">
              The dashboard is ready. Check the test pages for backend connectivity.
            </p>
          </div>
        </div>
        
        <div className="space-y-4">
          <a 
            href="/test" 
            className="inline-block bg-yellow-400 text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-yellow-500 transition-colors"
          >
            Test Backend Connection
          </a>
          
          <a 
            href="/simple" 
            className="inline-block bg-gray-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors ml-4"
          >
            Simple Test Page
          </a>
        </div>
      </div>
    </div>
  );
} 