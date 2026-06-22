"""
Google PageSpeed Insights (PSI) client.

PSI wraps real Lighthouse audits and is free for light usage without an API
key (a key only raises your rate limit — see
https://developers.google.com/speed/docs/insights/v5/get-started). This
gives us genuine performance/accessibility/seo/best-practices scores
instead of a hand-rolled heuristic.

Caveats worth knowing:
  - PSI runs Lighthouse against the LIVE site over the network, so it's
    slower than a local check (often 5-20 seconds) and can occasionally
    time out or rate-limit under heavy use. The orchestrator in
    analyzer.py treats a PSI failure as non-fatal and falls back to a
    lightweight heuristic so the whole report doesn't fail because of one
    flaky third-party call.
  - PSI returns a single overall "loading experience" but the per-category
    scores (performance, accessibility, seo, best-practices) are what we
    actually want here.
"""
import httpx

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"


class PageSpeedError(Exception):
    pass


def run_pagespeed(url: str, api_key: str | None = None, timeout: float = 30.0) -> dict:
    """
    Returns a dict with performance_score, accessibility_score, seo_score,
    best_practices_score (all 0-100 ints), and loading_speed_ms — or raises
    PageSpeedError if the call fails for any reason.
    """
    params = {
        "url": url,
        "category": ["PERFORMANCE", "ACCESSIBILITY", "SEO", "BEST_PRACTICES"],
        "strategy": "mobile",
    }
    if api_key:
        params["key"] = api_key

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.get(PSI_ENDPOINT, params=params)
    except httpx.HTTPError as exc:
        raise PageSpeedError(f"Network error calling PageSpeed Insights: {exc}") from exc

    if resp.status_code != 200:
        raise PageSpeedError(f"PageSpeed Insights returned {resp.status_code}: {resp.text[:300]}")

    data = resp.json()
    categories = data.get("lighthouseResult", {}).get("categories", {})

    def score_of(key: str) -> int | None:
        cat = categories.get(key)
        if not cat or cat.get("score") is None:
            return None
        return round(cat["score"] * 100)

    audits = data.get("lighthouseResult", {}).get("audits", {})
    # "interactive" (Time to Interactive) is a reasonable proxy for
    # perceived loading speed, given in milliseconds.
    interactive_ms = audits.get("interactive", {}).get("numericValue")

    return {
        "performance_score": score_of("performance"),
        "accessibility_score": score_of("accessibility"),
        "seo_score": score_of("seo"),
        "best_practices_score": score_of("best-practices"),
        "loading_speed_ms": round(interactive_ms) if interactive_ms is not None else None,
    }
