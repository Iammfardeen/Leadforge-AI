-- LOCAL DOCKER DEV ONLY.
-- When running against real Supabase (staging/production), this file is
-- NOT needed and should NOT be run — Supabase already provides a full
-- `auth` schema with its own auth.users table, triggers, and RLS support.
--
-- This file exists purely so `docker compose up` against plain Postgres
-- (no Supabase) has a minimal `auth.users` table for 0001_init.sql's
-- foreign keys and trigger to attach to, letting you test the schema
-- and backend locally without a Supabase project.
--
-- Runs first (0000) because 0001_init.sql references auth.users.

create schema if not exists auth;

create table if not exists auth.users (
  id uuid primary key default gen_random_uuid(),
  email text unique,
  encrypted_password text,
  created_at timestamptz not null default now()
);
