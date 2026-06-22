import { createSupabaseBrowserClient } from "@/lib/supabase/client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

/**
 * Calls the FastAPI backend at /api/v1/{path}, attaching the current
 * Supabase session's access token as a Bearer header. Use from Client
 * Components; for Server Components, fetch the session server-side instead.
 */
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const supabase = createSupabaseBrowserClient();
  const { data: { session } } = await supabase.auth.getSession();

  const res = await fetch(`${API_BASE_URL}/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(body.detail ?? "Request failed", res.status);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json();
}
