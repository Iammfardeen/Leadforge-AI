# LeadForge AI

An AI-powered lead generation and sales pipeline tool for freelance web developers: find local businesses that need a new website, analyze their current site, generate personalized outreach, and manage the deal through to close.

**Current status: Foundation phase.** This commit gets the full stack running end-to-end — Docker Compose, database schema + auth, every sidebar page reachable, and a real API contract between frontend and backend — with feature logic stubbed where noted. See [Implementation status](#implementation-status) below for exactly what's real vs. stubbed.

---

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), React, TypeScript, Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| Database | Postgres (Supabase in production, plain Postgres container locally) |
| Auth | Supabase Auth |
| AI | Groq (hosted, free tier) running Llama 3.3 70B — swapped in from a local Ollama container so the AI features work on a free, always-on deploy without a machine running 24/7. See [AI backend](#ai-backend) below. |
| Charts | Recharts |
| Local dev | Docker Compose |
| Deployment | Vercel (frontend) + Railway/Render (backend) + Supabase (DB/auth) |

Everything here is free / open-source. The one paid dependency is the **Google Places API** for Lead Finder — it has a monthly free credit, then bills per request, and you supply your own key (see [Lead Finder data source](#lead-finder-data-source) below for why).

---

## Quick start (local, Docker Compose)

1. **Copy environment files:**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

2. **Get a free Groq API key** (powers AI Report, Mockup, WhatsApp Generator):
   - Sign up at [console.groq.com](https://console.groq.com) — no credit card needed
   - Create an API key, paste it into `backend/.env` as `GROQ_API_KEY`

3. **Set up a free Supabase project** (or skip this for now — see note below):
   - Create a project at [supabase.com](https://supabase.com)
   - Go to Settings → API and copy `Project URL`, `anon public key`, `service_role key`
   - Go to Settings → API → JWT Settings and copy the `JWT Secret`
   - Paste these into `backend/.env` and `frontend/.env.local`
   - Run the SQL in `database/migrations/0001_init.sql`, then `0002_rls.sql`, then `0003_add_psi_key.sql` in the Supabase SQL Editor (in that order — skip `0000_local_dev_auth_stub.sql`, that's only for plain-Postgres local dev without Supabase)

   > **Don't have a Supabase project yet?** You can still run `docker compose up` — the `db` container runs plain Postgres and auto-applies all three migrations (including the `0000` auth stub) on first start. Auth won't work end-to-end without real Supabase Auth, but the API, schema, and every page will load.

4. **Start everything:**
   ```bash
   docker compose up
   ```
   No model download anymore — the `ollama` container is no longer started by default (kept behind a Compose profile if you ever want a fully local/offline setup instead). Startup is fast since AI calls go straight to Groq's hosted API.

5. **Open the app:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

6. **Add your Google Places API key** in Settings → API Keys to make Lead Finder return real results. Get a free-tier key at [developers.google.com/maps/documentation/places/web-service/get-api-key](https://developers.google.com/maps/documentation/places/web-service/get-api-key).

---

## Project structure

```
leadforge-ai/
├── frontend/                 Next.js app
│   └── src/
│       ├── app/
│       │   ├── (auth)/       login, signup
│       │   ├── (dashboard)/  all 10 sidebar pages, share a layout
│       │   └── api/auth/     Supabase auth callback route
│       ├── components/
│       │   ├── layout/       Sidebar, Topbar
│       │   └── ui/           Card, Badge, ScoreRing, EmptyState, Skeleton
│       ├── lib/               Supabase clients, API client, nav config, utils
│       └── middleware.ts     route protection + session refresh
├── backend/                   FastAPI app
│   └── app/
│       ├── api/routes/        one router per feature (leads, analyzer, ai_reports,
│       │                       mockups, screenshots, whatsapp, proposals, crm, reports, settings)
│       ├── services/           business logic per feature (places.py is fully
│       │                       implemented; others are documented stubs — see below)
│       ├── core/                config, auth (JWT verification)
│       ├── models/              Pydantic schemas
│       └── db/                  Supabase client factory
├── database/
│   └── migrations/
│       ├── 0000_local_dev_auth_stub.sql   plain-Postgres-only, skip on real Supabase
│       ├── 0001_init.sql                  all tables, triggers, indexes
│       └── 0002_rls.sql                   row-level security policies
└── docker-compose.yml          db + backend + frontend
```

---

## Implementation status

**Fully implemented:**
- Database schema (10 tables) + Row Level Security policies, scoped so every user only ever sees their own data
- Supabase Auth flow: signup, login, logout, session refresh, protected routes via middleware
- FastAPI backend with a real route + Pydantic model for every feature, JWT verification on every endpoint
- Google Places integration for Lead Finder (`backend/app/services/places.py`) — see caveats below
- **Website Analyzer** (`backend/app/services/analyzer.py` + `analyzer_ssl.py`, `analyzer_pagespeed.py`, `analyzer_html.py`, `analyzer_links.py`) — a real audit combining:
  - SSL/HTTPS validity (direct TLS handshake check)
  - Performance, SEO, and Accessibility scores from Google PageSpeed Insights (real Lighthouse data, free without an API key for light use — add one in Settings to raise the rate limit)
  - HTML heuristics: favicon, meta tags, Open Graph, schema.org/JSON-LD, contact form, WhatsApp click-to-chat button, Google Maps embed, social links, dark-mode signal, responsive viewport
  - Broken link check (same-domain, depth 1, capped at 25 links)
  - Image optimization scoring (missing alt text / missing width+height)
  - A weighted `overall_score` (0-100) combining all of the above
  - Every third-party call (PageSpeed, link checks) degrades gracefully — a failure there doesn't fail the whole report, it just reduces what that report can show
- Lead Finder → save lead → Website Analyzer → AI Report → AI Website Mockup → WhatsApp Generator is a complete, working path end to end
- **AI Website Mockup** (`backend/app/services/mockup.py`) — generates a real, rendered homepage wireframe (not just a description) plus an image-generation prompt for the hero visual:
  - Uses two separate Groq calls (short image prompt, then a dedicated HTML generation call) rather than one combined response — smaller models reliably truncate or mis-escape long HTML when it's bundled into a single JSON object alongside other fields
  - Validates the returned HTML (real `<!DOCTYPE html>`, closing `</html>`, the required Tailwind CDN script tag, minimum length) and retries once with a corrective prompt if the first attempt fails
  - Strips markdown code fences automatically — a very common local-model habit of wrapping HTML output in ` ```html ` blocks despite being told not to
  - Reuses the latest AI Report's suggested colors/fonts/style for this lead if one exists, so the Mockup stays visually consistent with the AI Report rather than independently inventing a different palette
  - Frontend renders the HTML in a sandboxed iframe (`sandbox="allow-scripts"`, deliberately without `allow-same-origin`) so the Tailwind CDN script can execute and style the page, while the AI-generated content still can't read cookies, access localStorage, or reach the parent page
- **AI Report** (`backend/app/services/ai_report.py`) — generates a real business summary, weaknesses, improvements, lost-customer/revenue estimates, and a suggested redesign direction (features, colors, fonts, style) via Groq's hosted Llama 3.3 70B. Built with:
  - A schema-explicit prompt that gives the model every required key, type, and content guidance up front
  - Strict post-generation validation (right keys, right types, non-empty lists, valid hex colors) since Groq's JSON mode guarantees valid JSON but not the *right* JSON
  - One automatic corrective retry if validation fails, telling the model exactly what was wrong rather than just trying again blind
  - Works whether or not the lead has a website analysis yet — it adapts the prompt accordingly rather than failing
- **WhatsApp Generator** (`backend/app/services/whatsapp.py`) — generates a personalized outreach message via Groq across 12 combinations of tone (professional/friendly/luxury) × length (short/long) × language (English/Hindi):
  - Adapts the prompt based on whether the lead already has a website (and its weaknesses) or none at all
  - Falls back to a deterministic, hand-written template if Groq is unreachable (e.g. free-tier rate limit hit), so the feature still produces something usable rather than failing outright
  - **Never sends anything** — no WhatsApp Business API client exists anywhere in this codebase. The route only returns text; the frontend only offers a Copy button. This is enforced as a hard rule, not a missing feature.
  - Frontend includes full message history per lead and a working clipboard Copy button
- Full dashboard shell: sidebar, top bar, all 10 pages reachable and laid out
- Lead Score visual component (the ring badge), reused across the app
- Docker Compose: Postgres, backend, frontend (AI calls go to Groq's hosted API, not a local container)

**Stubbed, with the exact contract locked in** (each raises `NotImplementedError` with a comment describing the planned implementation — see the file for specifics):
- `services/screenshot.py` — Playwright screenshot capture
- `services/proposal_pdf.py` — PDF rendering for proposals

These all have working routes, request/response shapes, and database writes already wired — only the core algorithm inside each service function is left for the next phase. The frontend pages for these features render real empty states pointing at this.

---

## AI backend

AI Report, AI Website Mockup, and WhatsApp Generator all call Groq's hosted API (`backend/app/services/ollama_client.py` — kept its old filename and function names so no other file had to change) instead of a local Ollama container. Why: free hosts don't have anywhere near enough RAM to run Llama 3 locally, so this lets the whole app run 24/7 on free tiers with nothing on your own machine.

- Get a free key at [console.groq.com](https://console.groq.com) (no credit card) and set `GROQ_API_KEY` in `backend/.env` (local) or your host's environment variables (production).
- Default model is `llama-3.3-70b-versatile`. `llama-3.1-8b-instant` is also wired up in Settings → AI model if you hit free-tier rate limits and want higher throughput at lower quality.
- Free tier limits (subject to change, check [console.groq.com](https://console.groq.com) for current numbers): roughly 1,000 requests/day and 30 requests/minute per model — plenty for personal use or demos, tight for many simultaneous users.
- Prefer to stay fully local/offline instead? The original Ollama container is still in `docker-compose.yml` behind a profile: `docker compose --profile legacy-local-ollama up`. You'd need to revert `ollama_client.py` to call Ollama's native `/api/generate` endpoint again instead of Groq's — it's one small, isolated file, the change was deliberately contained there.

---

## Lead Finder data source

The brief asks for owner name, email, Instagram, and Facebook alongside business listings. Worth being upfront about what's actually obtainable for free:

- **Available via Google Places API:** business name, address, phone, website, rating, review count, place ID.
- **Not available via Google Places, and not fabricated by this app:** owner name, email address, Instagram/Facebook links. These would require scraping the business's own website (unreliable — many small businesses don't list this anywhere) or a paid data enrichment service. `services/places.py` returns `null` for these rather than guessing.
- **Business age:** Places doesn't expose this either; left null unless a future heuristic (e.g. domain registration lookup) is added.

You'll need your own Google Places API key (Settings → API Keys) — it has a monthly free credit, then bills per request after that.

---

## What this app deliberately does NOT do

Per the original brief: **WhatsApp messages are generated, never sent automatically.** There is no WhatsApp Business API integration anywhere in this codebase. The WhatsApp Generator page only produces text and a Copy button.
