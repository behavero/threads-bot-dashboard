/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_BACKEND_URL: 'https://threads-bot-dashboard-3.onrender.com',
    NEXT_PUBLIC_SUPABASE_URL: 'https://perwbmtwutwzsvlirwik.supabase.co',
    NEXT_PUBLIC_SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBlcndibXR3dXR3enN2bGlyd2lrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0MDU1ODIsImV4cCI6MjA2OTk4MTU4Mn0.ACJ6v7w4brocGyhC3hlsWI_huE3-3kSdQjLSCijw56o',
  },
};

module.exports = nextConfig; 