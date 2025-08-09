import { API_BASE } from '@/lib/config'
import type { Account, AccountUpdatePayload, TestPostResponse } from '@/types/accounts'

// Base API response type
type ApiResponse<T = any> = {
  ok: boolean;
  error?: string;
  message?: string;
} & T;

// Account API functions
export async function fetchAccounts(): Promise<Account[]> {
  const response = await fetch(`${API_BASE}/api/accounts`);
  const data: ApiResponse<{ accounts: Account[] }> = await response.json();
  
  if (!data.ok) {
    throw new Error(data.error || 'Failed to fetch accounts');
  }
  
  return data.accounts || [];
}

export async function patchAccount(
  id: string, 
  payload: AccountUpdatePayload
): Promise<void> {
  const response = await fetch(`${API_BASE}/api/accounts/${id}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  
  const data: ApiResponse = await response.json();
  
  if (!data.ok) {
    throw new Error(data.error || 'Failed to update account');
  }
}

export async function updateAutopilot(
  id: string, 
  enabled: boolean
): Promise<{ autopilot_enabled: boolean; next_run_at?: string | null }> {
  const response = await fetch(`${API_BASE}/api/accounts/${id}/autopilot`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ enabled }),
  });
  
  const data: ApiResponse<{ autopilot_enabled: boolean; next_run_at?: string | null }> = await response.json();
  
  if (!data.ok) {
    throw new Error(data.error || 'Failed to update autopilot');
  }
  
  return {
    autopilot_enabled: data.autopilot_enabled,
    next_run_at: data.next_run_at
  };
}

export async function updateCadence(
  id: string, 
  minutes: number
): Promise<{ cadence_minutes: number; next_run_at?: string | null }> {
  const response = await fetch(`${API_BASE}/api/accounts/${id}/cadence`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ minutes }),
  });
  
  const data: ApiResponse<{ cadence_minutes: number; next_run_at?: string | null }> = await response.json();
  
  if (!data.ok) {
    throw new Error(data.error || 'Failed to update cadence');
  }
  
  return {
    cadence_minutes: data.cadence_minutes,
    next_run_at: data.next_run_at
  };
}

export function startOAuth(accountId: string): void {
  // Direct redirect to backend OAuth endpoint with reconnect purpose - backend will handle the redirect to Meta
  window.location.href = `${API_BASE}/auth/meta/start?account_id=${accountId}&purpose=reconnect`;
}

export async function testPost(accountId: string): Promise<TestPostResponse> {
  const response = await fetch(`${API_BASE}/api/threads/post`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      account_id: accountId, 
      use_random: true,
      is_test: true
    }),
  });
  
  const data: TestPostResponse = await response.json();
  return data;
}

// Session upload functionality moved to Images page if needed
