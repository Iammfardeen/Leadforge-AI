"""
Website Analyzer engine.

Combines four independent checks into one report matching the
website_analyses table:

  1. SSL/HTTPS validity        (analyzer_ssl.py)       — local, fast, free
  2. PageSpeed Insights        (analyzer_pagespeed.py) — real Lighthouse data, free tier
  3. HTML heuristics           (analyzer_html.py)      — favicon/meta/OG/schema/contact/etc
  4. Broken link check         (analyzer_links.py)     — same-domain, depth 1, capped

Each step is independently fault-tolerant: if PageSpeed Insights times out
or rate-limits (it's a third-party network call, after all), the report
still completes using a lightweight fallback rather than failing outright.
A failed broken-link check just reports 0 rather than blocking the report.

overall_score is a weighted average:
  performance 25%, seo 25%, accessibility 20%, image_optimization 10%,
  plus a flat structural bonus/penalty for the boolean feature checks
  (ssl, contact form, responsive, etc), clamped to 0-100.
"""
import time

from app.services import analyzer_html, analyzer_links, analyzer_pagespeed, analyzer_ssl

# Structural checks and their score weight when present (positive) — and
# implicitly, the penalty incurred when absent (since we sum only the
# present ones and compare against the max possible).
STRUCTURAL_CHECKS = {
    "has_ssl": 4,
    "is_https": 4,
    "is_responsive": 4,
    "has_favicon": 2,
    "has_meta_tags": 3,
    "has_open_graph": 2,
    "has_schema_markup": 2,
    "has_contact_form": 3,
    "has_whatsapp_button": 2,
    "has_google_maps_embed": 2,
    "has_social_links": 2,
}
MAX_STRUCTURAL_POINTS = sum(STRUCTURAL_CHECKS.values())  # 30


def _fallback_performance(elapsed_ms: int) -> dict:
    """
    Used only if PageSpeed Insights fails. A simple response-time-based
    heuristic so the report still has *something* for these fields rather
    than nulls — clearly less rigorous than real Lighthouse data, which is
    why PSI is tried first.
    """
    if elapsed_ms < 800:
        perf = 90
    elif elapsed_ms < 1800:
        perf = 70
    elif elapsed_ms < 3500:
        perf = 50
    else:
        perf = 30

    return {
        "performance_score": perf,
        "accessibility_score": None,
        "seo_score": None,
        "best_practices_score": None,
        "loading_speed_ms": elapsed_ms,
    }


def _compute_overall_score(perf, seo, a11y, img: int, structural_points: int) -> int:
    weighted_parts = []
    if perf is not None:
        weighted_parts.append((perf, 0.25))
    if seo is not None:
        weighted_parts.append((seo, 0.25))
    if a11y is not None:
        weighted_parts.append((a11y, 0.20))
    weighted_parts.append((img, 0.10))

    total_weight = sum(w for _, w in weighted_parts)
    base_score = sum(score * w for score, w in weighted_parts) / total_weight if total_weight else 50

    structural_ratio = structural_points / MAX_STRUCTURAL_POINTS  # 0.0-1.0
    structural_adjustment = (structural_ratio - 0.5) * 40  # -20 to +20

    final = base_score * 0.8 + (base_score + structural_adjustment) * 0.2
    return max(0, min(100, round(final)))


def run_analysis(website_url: str, google_psi_api_key: str | None = None) -> dict:
    if not website_url.startswith(("http://", "https://")):
        website_url = f"https://{website_url}"

    # --- 1. SSL/HTTPS ---
    ssl_result = analyzer_ssl.check_ssl(website_url)

    # --- 2. Fetch HTML once, time it, reuse for heuristics + link check ---
    start = time.monotonic()
    try:
        final_url, html = analyzer_html.fetch_html(website_url)
        elapsed_ms = round((time.monotonic() - start) * 1000)
        fetch_error = None
    except analyzer_html.FetchError as exc:
        final_url, html, elapsed_ms = website_url, "", None
        fetch_error = str(exc)

    html_result = analyzer_html.analyze_html(html, final_url) if html else {
        "has_favicon": False, "has_meta_tags": False, "has_open_graph": False,
        "has_schema_markup": False, "has_contact_form": False, "has_whatsapp_button": False,
        "has_google_maps_embed": False, "has_social_links": False, "has_dark_mode": False,
        "is_responsive": False, "image_optimization_score": 0,
        "_same_domain_links": [], "_found_social_domains": [],
    }

    # --- 3. PageSpeed Insights (fault-tolerant) ---
    psi_error = None
    try:
        psi_result = analyzer_pagespeed.run_pagespeed(final_url, api_key=google_psi_api_key)
    except analyzer_pagespeed.PageSpeedError as exc:
        psi_error = str(exc)
        psi_result = _fallback_performance(elapsed_ms or 5000)

    # --- 4. Broken links (fault-tolerant, skipped entirely if fetch failed) ---
    broken_links_count = 0
    if html:
        try:
            broken_links_count = analyzer_links.count_broken_links(final_url, html_result["_same_domain_links"])
        except Exception:
            broken_links_count = 0

    # --- Assemble structural score contribution ---
    structural_flags = {
        "has_ssl": ssl_result["has_ssl"],
        "is_https": ssl_result["is_https"],
        "is_responsive": html_result["is_responsive"],
        "has_favicon": html_result["has_favicon"],
        "has_meta_tags": html_result["has_meta_tags"],
        "has_open_graph": html_result["has_open_graph"],
        "has_schema_markup": html_result["has_schema_markup"],
        "has_contact_form": html_result["has_contact_form"],
        "has_whatsapp_button": html_result["has_whatsapp_button"],
        "has_google_maps_embed": html_result["has_google_maps_embed"],
        "has_social_links": html_result["has_social_links"],
    }
    structural_points = sum(STRUCTURAL_CHECKS[k] for k, present in structural_flags.items() if present)

    overall_score = _compute_overall_score(
        perf=psi_result["performance_score"],
        seo=psi_result["seo_score"],
        a11y=psi_result["accessibility_score"],
        img=html_result["image_optimization_score"],
        structural_points=structural_points,
    )

    return {
        "has_ssl": ssl_result["has_ssl"],
        "is_https": ssl_result["is_https"],
        "performance_score": psi_result["performance_score"],
        "seo_score": psi_result["seo_score"],
        "accessibility_score": psi_result["accessibility_score"],
        "overall_score": overall_score,

        "broken_links_count": broken_links_count,
        "is_responsive": html_result["is_responsive"],
        "has_favicon": html_result["has_favicon"],
        "has_meta_tags": html_result["has_meta_tags"],
        "has_open_graph": html_result["has_open_graph"],
        "has_schema_markup": html_result["has_schema_markup"],
        "has_contact_form": html_result["has_contact_form"],
        "has_whatsapp_button": html_result["has_whatsapp_button"],
        "has_google_maps_embed": html_result["has_google_maps_embed"],
        "has_social_links": html_result["has_social_links"],
        "has_dark_mode": html_result["has_dark_mode"],
        "loading_speed_ms": psi_result["loading_speed_ms"],
        "image_optimization_score": html_result["image_optimization_score"],

        "raw_report": {
            "final_url": final_url,
            "fetch_error": fetch_error,
            "pagespeed_error": psi_error,
            "best_practices_score": psi_result.get("best_practices_score"),
            "found_social_domains": html_result["_found_social_domains"],
            "structural_points": structural_points,
            "structural_points_max": MAX_STRUCTURAL_POINTS,
        },
    }
