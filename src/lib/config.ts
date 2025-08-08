/**
 * API Configuration
 * Centralized configuration for all API endpoints
 */

export const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL ?? 'https://threads-bot-dashboard-3.onrender.com';

export const META_CONFIG = {
  APP_ID: process.env.NEXT_PUBLIC_META_APP_ID ?? '1827652407826369',
  OAUTH_REDIRECT_URI: process.env.NEXT_PUBLIC_OAUTH_REDIRECT_URI ?? 'https://threads-bot-dashboard.vercel.app/api/auth/meta/callback',
  APP_BASE_URL: process.env.NEXT_PUBLIC_APP_BASE_URL ?? 'https://threads-bot-dashboard.vercel.app',
};

export const API_ENDPOINTS = {
  // Auth endpoints
  AUTH_START: `${API_BASE}/auth/meta/start`,
  AUTH_CALLBACK: `${API_BASE}/auth/meta/callback`,
  AUTH_REFRESH: `${API_BASE}/auth/meta/refresh`,
  
  // Account endpoints
  ACCOUNTS: `${API_BASE}/api/accounts`,
  ACCOUNTS_LOGIN: `${API_BASE}/api/accounts/login`,
  ACCOUNTS_VERIFY: `${API_BASE}/api/accounts/verify`,
  
  // Threads endpoints
  THREADS_POST: `${API_BASE}/threads/post`,
  THREADS_SCHEDULE: `${API_BASE}/threads/schedule`,
  THREADS_ACCOUNTS: `${API_BASE}/threads/accounts`,
  
  // Scheduler endpoints
  SCHEDULER_RUN: `${API_BASE}/scheduler/run`,
  SCHEDULER_STATUS: `${API_BASE}/scheduler/status`,
  
  // Stats endpoints
  STATS_ENGAGEMENT: `${API_BASE}/api/stats/engagement`,
  STATS_OVERVIEW: `${API_BASE}/api/stats/overview`,
  STATS_ACCOUNTS: `${API_BASE}/api/stats/accounts`,
  
  // Content endpoints
  CAPTIONS: `${API_BASE}/api/captions`,
  IMAGES: `${API_BASE}/api/images`,
  
  // Health endpoint
  HEALTH: `${API_BASE}/api/health`,
};

export const THREADS_SCOPES = [
  'threads_basic',
  'threads_content_publish',
  'threads_manage_insights',
  'threads_manage_replies',
  'threads_read_replies',
  'threads_keyword_search',
  'threads_manage_mentions',
  'threads_delete',
  'threads_location_tagging',
  'threads_profile_discovery',
] as const;

export type ThreadsScope = typeof THREADS_SCOPES[number];
