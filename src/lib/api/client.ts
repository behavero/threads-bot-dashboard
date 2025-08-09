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

export function startOAuth(accountId: string): void {
  window.location.href = `${API_BASE}/auth/meta/start?account_id=${accountId}`;
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

// Session upload
export async function uploadSession(accountId: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.append('session_file', file);
  
  const response = await fetch(`${API_BASE}/api/accounts/${accountId}/session`, {
    method: 'POST',
    body: formData,
  });
  
  const data: ApiResponse = await response.json();
  
  if (!data.ok) {
    throw new Error(data.error || 'Failed to upload session');
  }
}
