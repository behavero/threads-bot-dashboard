export type Account = {
  id: string;
  username: string;
  description?: string;
  threads_connected: boolean;
  autopilot_enabled: boolean;
  cadence_minutes: number;
  next_run_at?: string | null;
  last_posted_at?: string | null;
  connection_status: 'connected_session' | 'connected_official' | 'disconnected';
};

export type AccountUpdatePayload = Partial<{
  autopilot_enabled: boolean;
  cadence_minutes: number;
  description: string;
}>;

export type TestPostResponse = {
  ok: boolean;
  post?: {
    account_id: string;
    username: string;
    text: string;
    image_url?: string;
    posted_at: string;
    status: string;
    method: string;
  };
  message?: string;
  error?: string;
};
