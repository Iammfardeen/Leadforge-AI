-- LeadForge AI — Initial schema
-- Target: Supabase Postgres (also runs on plain Postgres for local Docker dev)
-- Run order: 0001_init.sql -> 0002_rls.sql

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- ============================================================================
-- ENUM TYPES
-- ============================================================================
create type lead_status as enum (
  'new',
  'contacted',
  'replied',
  'interested',
  'meeting',
  'proposal_sent',
  'won',
  'lost',
  'archived'
);

create type message_tone as enum ('professional', 'friendly', 'luxury');
create type message_length as enum ('short', 'long');
create type message_language as enum ('en', 'hi');

create type proposal_status as enum ('draft', 'sent', 'viewed', 'accepted', 'declined', 'expired');

-- ============================================================================
-- PROFILES
-- Mirrors auth.users (Supabase managed). One row per signed-up user.
-- ============================================================================
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  business_name text,
  brand_logo_url text,
  theme text not null default 'dark' check (theme in ('light', 'dark')),
  ai_model text not null default 'llama-3.3-70b-versatile',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Auto-create a profile row whenever a new auth user is created.
create function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, business_name)
  values (new.id, null);
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ============================================================================
-- USER SETTINGS (api keys, smtp, etc. — never expose raw secrets to client queries)
-- ============================================================================
create table public.user_settings (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  google_places_api_key text,
  supabase_service_key text,
  smtp_host text,
  smtp_port int,
  smtp_username text,
  smtp_password text,
  ollama_base_url text not null default 'http://localhost:11434',
  updated_at timestamptz not null default now()
);

-- ============================================================================
-- LEADS
-- ============================================================================
create table public.leads (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid not null references public.profiles(id) on delete cascade,

  business_name text not null,
  owner_name text,
  phone text,
  email text,
  website_url text,
  google_rating numeric(2,1),
  review_count int,
  address text,
  city text,
  category text,
  business_age_years int,
  has_website boolean not null default false,
  instagram_url text,
  facebook_url text,

  google_place_id text,

  status lead_status not null default 'new',
  notes text,
  tags text[] not null default '{}',
  lead_score int check (lead_score between 0 and 100),

  follow_up_at timestamptz,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index leads_user_id_idx on public.leads(user_id);
create index leads_status_idx on public.leads(status);
create index leads_city_category_idx on public.leads(city, category);
create index leads_score_idx on public.leads(lead_score);
create unique index leads_user_place_unique on public.leads(user_id, google_place_id)
  where google_place_id is not null;

-- ============================================================================
-- WEBSITE ANALYSES
-- One row per analysis run (keeps history; latest = most recent created_at)
-- ============================================================================
create table public.website_analyses (
  id uuid primary key default uuid_generate_v4(),
  lead_id uuid not null references public.leads(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,

  has_ssl boolean,
  is_https boolean,
  performance_score int check (performance_score between 0 and 100),
  seo_score int check (seo_score between 0 and 100),
  accessibility_score int check (accessibility_score between 0 and 100),
  overall_score int check (overall_score between 0 and 100),

  broken_links_count int,
  is_responsive boolean,
  has_favicon boolean,
  has_meta_tags boolean,
  has_open_graph boolean,
  has_schema_markup boolean,
  has_contact_form boolean,
  has_whatsapp_button boolean,
  has_google_maps_embed boolean,
  has_social_links boolean,
  has_dark_mode boolean,
  loading_speed_ms int,
  image_optimization_score int check (image_optimization_score between 0 and 100),

  raw_report jsonb,

  created_at timestamptz not null default now()
);

create index website_analyses_lead_id_idx on public.website_analyses(lead_id);
create index website_analyses_user_id_idx on public.website_analyses(user_id);

-- ============================================================================
-- AI REPORTS
-- AI-generated narrative analysis tied to a specific website_analysis run
-- ============================================================================
create table public.ai_reports (
  id uuid primary key default uuid_generate_v4(),
  lead_id uuid not null references public.leads(id) on delete cascade,
  analysis_id uuid references public.website_analyses(id) on delete set null,
  user_id uuid not null references public.profiles(id) on delete cascade,

  business_summary text,
  weaknesses text[],
  improvements text[],
  estimated_lost_customers_per_month int,
  estimated_revenue_increase_monthly numeric(12,2),
  suggested_features text[],
  suggested_colors text[],
  suggested_fonts text[],
  suggested_design_style text,

  model_used text not null default 'llama-3.3-70b-versatile',
  created_at timestamptz not null default now()
);

create index ai_reports_lead_id_idx on public.ai_reports(lead_id);

-- ============================================================================
-- WEBSITE MOCKUPS (AI redesign wireframes)
-- ============================================================================
create table public.website_mockups (
  id uuid primary key default uuid_generate_v4(),
  lead_id uuid not null references public.leads(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,

  sections text[] not null default '{hero,services,gallery,testimonials,about,contact,footer}',
  image_prompt text,
  html_preview text,

  created_at timestamptz not null default now()
);

create index website_mockups_lead_id_idx on public.website_mockups(lead_id);

-- ============================================================================
-- SCREENSHOTS
-- ============================================================================
create table public.screenshots (
  id uuid primary key default uuid_generate_v4(),
  lead_id uuid not null references public.leads(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,

  storage_path text not null,
  page_url text not null,
  capture_type text not null default 'full_page' check (capture_type in ('full_page', 'viewport', 'mobile')),

  created_at timestamptz not null default now()
);

create index screenshots_lead_id_idx on public.screenshots(lead_id);

-- ============================================================================
-- WHATSAPP MESSAGES (generated drafts — never sent by the app)
-- ============================================================================
create table public.whatsapp_messages (
  id uuid primary key default uuid_generate_v4(),
  lead_id uuid not null references public.leads(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,

  tone message_tone not null default 'professional',
  length message_length not null default 'short',
  language message_language not null default 'en',
  content text not null,

  created_at timestamptz not null default now()
);

create index whatsapp_messages_lead_id_idx on public.whatsapp_messages(lead_id);

-- ============================================================================
-- PROPOSALS
-- ============================================================================
create table public.proposals (
  id uuid primary key default uuid_generate_v4(),
  lead_id uuid not null references public.leads(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,

  pricing jsonb,
  timeline jsonb,
  deliverables text[],
  hosting_details text,
  maintenance_details text,
  payment_terms text,

  status proposal_status not null default 'draft',
  pdf_storage_path text,
  signed_at timestamptz,
  signature_data_url text,

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index proposals_lead_id_idx on public.proposals(lead_id);
create index proposals_status_idx on public.proposals(status);

-- ============================================================================
-- ACTIVITY LOG (powers CRM timeline + reports)
-- ============================================================================
create table public.activity_log (
  id uuid primary key default uuid_generate_v4(),
  lead_id uuid not null references public.leads(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,

  event_type text not null,
  description text,
  metadata jsonb,

  created_at timestamptz not null default now()
);

create index activity_log_lead_id_idx on public.activity_log(lead_id);
create index activity_log_created_at_idx on public.activity_log(created_at);

-- ============================================================================
-- updated_at triggers
-- ============================================================================
create function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger leads_set_updated_at before update on public.leads
  for each row execute procedure public.set_updated_at();

create trigger proposals_set_updated_at before update on public.proposals
  for each row execute procedure public.set_updated_at();

create trigger profiles_set_updated_at before update on public.profiles
  for each row execute procedure public.set_updated_at();
