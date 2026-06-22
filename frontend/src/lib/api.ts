import { createSupabaseBrowserClient } from "@/lib/supabase/client";

// Explicitly log the environment variable to verify it's not undefined
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_BASE_URL) {
  console.error("CRITICAL: NEXT_PUBLIC_API_URL is undefined in this environment!");
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const supabase = createSupabaseBrowserClient();
  const { data: { session } } = await supabase.auth.getSession();

  const url = `${API_BASE_URL ?? "https://leadforge-ai-u6sc.onrender.com"}/api/v1${path}`;
  
  console.log("Attempting request to:", url);

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    console.error(`API Error ${res.status}:`, await res.text().catch(() => "No error body"));
    throw new ApiError("Request failed", res.status);
  }

  return res.status === 204 ? (undefined as T) : res.json();
}
