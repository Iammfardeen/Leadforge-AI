"""
Screenshot capture — STUB (foundation phase).

Planned implementation: use Playwright (Python) headless Chromium to load
the target URL, wait for network idle, capture a full-page PNG, upload it
to Supabase Storage bucket STORAGE_BUCKET_SCREENSHOTS under
`{user_id}/{lead_id}/{timestamp}.png`, and return the storage path.

This requires the `playwright` Python package + `playwright install chromium`
in the backend Docker image (already declared in docker/backend.Dockerfile).

Output dict must contain:
  storage_path: str
  capture_type: str  ("full_page" | "viewport" | "mobile")
"""


def capture(website_url: str) -> dict:
    raise NotImplementedError("Screenshot capture will be implemented in the feature-build phase")
