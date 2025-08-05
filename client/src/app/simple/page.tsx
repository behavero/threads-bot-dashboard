export default function SimplePage() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-8">Simple Test Page</h1>
        <p className="text-xl text-gray-300 mb-4">If you can see this, basic routing is working!</p>
        <div className="bg-gray-800 rounded-lg p-6 max-w-md mx-auto">
          <h2 className="text-2xl font-semibold mb-4">✅ Success!</h2>
          <p className="text-gray-400">
            The page is loading correctly. The 404 error might be related to:
          </p>
          <ul className="text-left text-sm text-gray-400 mt-4 space-y-2">
            <li>• Environment variables not set</li>
            <li>• Backend URL configuration</li>
            <li>• API endpoint issues</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 