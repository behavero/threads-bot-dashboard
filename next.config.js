/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    NEXT_PUBLIC_BACKEND_URL: 'https://threads-bot-dashboard-3.onrender.com',
    // Supabase variables are now automatically provided by Vercel integration
  },
};

module.exports = nextConfig; 