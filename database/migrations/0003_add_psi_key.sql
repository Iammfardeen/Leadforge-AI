-- Adds an optional Google PageSpeed Insights API key.
-- PSI works without a key for light usage; a key only raises the free rate
-- limit, so this column is nullable and the analyzer falls back gracefully
-- when it's empty.

alter table public.user_settings
  add column if not exists google_psi_api_key text;
