export const API_CONFIG = {
  BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000',
  SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL || '',
  SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '',
} as const;

export const API_ENDPOINTS = {
  ACCOUNTS: '/api/accounts',
  CAPTIONS: '/api/captions',
  IMAGES: '/api/images',
  SCHEDULE: '/api/schedule',
  LOGIN: '/api/auth/login',
  LOGOUT: '/api/auth/logout',
} as const; 