-- LeadForge AI — Row Level Security
-- Ensures every authenticated user can only read/write their own rows.
-- Run after 0001_init.sql

alter table public.profiles enable row level security;
alter table public.user_settings enable row level security;
alter table public.leads enable row level security;
alter table public.website_analyses enable row level security;
alter table public.ai_reports enable row level security;
alter table public.website_mockups enable row level security;
alter table public.screenshots enable row level security;
alter table public.whatsapp_messages enable row level security;
alter table public.proposals enable row level security;
alter table public.activity_log enable row level security;

-- PROFILES: a user can only see/update their own profile row
create policy "profiles_select_own" on public.profiles
  for select using (auth.uid() = id);
create policy "profiles_update_own" on public.profiles
  for update using (auth.uid() = id);

-- USER_SETTINGS
create policy "user_settings_select_own" on public.user_settings
  for select using (auth.uid() = user_id);
create policy "user_settings_upsert_own" on public.user_settings
  for insert with check (auth.uid() = user_id);
create policy "user_settings_update_own" on public.user_settings
  for update using (auth.uid() = user_id);

-- LEADS
create policy "leads_select_own" on public.leads
  for select using (auth.uid() = user_id);
create policy "leads_insert_own" on public.leads
  for insert with check (auth.uid() = user_id);
create policy "leads_update_own" on public.leads
  for update using (auth.uid() = user_id);
create policy "leads_delete_own" on public.leads
  for delete using (auth.uid() = user_id);

-- WEBSITE_ANALYSES
create policy "website_analyses_select_own" on public.website_analyses
  for select using (auth.uid() = user_id);
create policy "website_analyses_insert_own" on public.website_analyses
  for insert with check (auth.uid() = user_id);

-- AI_REPORTS
create policy "ai_reports_select_own" on public.ai_reports
  for select using (auth.uid() = user_id);
create policy "ai_reports_insert_own" on public.ai_reports
  for insert with check (auth.uid() = user_id);

-- WEBSITE_MOCKUPS
create policy "website_mockups_select_own" on public.website_mockups
  for select using (auth.uid() = user_id);
create policy "website_mockups_insert_own" on public.website_mockups
  for insert with check (auth.uid() = user_id);

-- SCREENSHOTS
create policy "screenshots_select_own" on public.screenshots
  for select using (auth.uid() = user_id);
create policy "screenshots_insert_own" on public.screenshots
  for insert with check (auth.uid() = user_id);

-- WHATSAPP_MESSAGES
create policy "whatsapp_messages_select_own" on public.whatsapp_messages
  for select using (auth.uid() = user_id);
create policy "whatsapp_messages_insert_own" on public.whatsapp_messages
  for insert with check (auth.uid() = user_id);

-- PROPOSALS
create policy "proposals_select_own" on public.proposals
  for select using (auth.uid() = user_id);
create policy "proposals_insert_own" on public.proposals
  for insert with check (auth.uid() = user_id);
create policy "proposals_update_own" on public.proposals
  for update using (auth.uid() = user_id);

-- ACTIVITY_LOG
create policy "activity_log_select_own" on public.activity_log
  for select using (auth.uid() = user_id);
create policy "activity_log_insert_own" on public.activity_log
  for insert with check (auth.uid() = user_id);
