"""
Supabase client factory.

Two clients are exposed:
- get_supabase(): uses the anon key, respects RLS (use for user-scoped reads
  when you already have a verified JWT to attach).
- get_supabase_admin(): uses the service role key, BYPASSES RLS. Only use
  this inside trusted backend operations (e.g. background jobs) where the
  user_id is explicitly and correctly filtered in the query itself.
"""
from functools import lru_cache

from supabase import Client, create_client

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_supabase() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


@lru_cache
def get_supabase_admin() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
