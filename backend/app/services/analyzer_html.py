"""
HTML heuristic checks.

PageSpeed Insights covers performance/accessibility/seo/best-practices, but
the brief also asks for several presence/absence checks that need to look
at the actual page markup: favicon, meta tags, Open Graph, schema.org
markup, contact form, WhatsApp click-to-chat button, embedded Google Maps,
social media links, and a dark-mode signal.

These are heuristics, not guarantees — e.g. a contact form built entirely
in JavaScript with no <form> tag in the initial HTML won't be detected
without executing JS (which would require a headless browser; out of scope
for this lightweight pass). Each check looks for the common, real-world
patterns small business sites actually use.
"""
import re

import httpx
from bs4 import BeautifulSoup

WHATSAPP_PATTERNS = (
    "wa.me/",
    "api.whatsapp.com/send",
    "web.whatsapp.com/send",
)

SOCIAL_DOMAINS = (
    "instagram.com",
    "facebook.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "youtube.com",
    "tiktok.com",
)

MAPS_EMBED_PATTERNS = (
    "google.com/maps/embed",
    "maps.google.com",
)


class FetchError(Exception):
    pass


def fetch_html(url: str, timeout: float = 15.0) -> tuple[str, str]:
    """Returns (final_url, html). Raises FetchError on any failure."""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; LeadForgeBot/1.0; +website-audit)"
    }
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
            resp = client.get(url)
    except httpx.HTTPError as exc:
        raise FetchError(f"Could not fetch {url}: {exc}") from exc

    if resp.status_code >= 400:
        raise FetchError(f"{url} returned HTTP {resp.status_code}")

    return str(resp.url), resp.text


def analyze_html(html: str, base_url: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    lower_html = html.lower()

    # --- Favicon ---
    has_favicon = bool(
        soup.find("link", rel=lambda v: v and "icon" in v.lower())
    )

    # --- Meta tags ---
    has_meta_description = bool(soup.find("meta", attrs={"name": "description"}))
    has_meta_viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
    has_meta_tags = has_meta_description and has_meta_viewport

    # --- Open Graph ---
    og_tags = soup.find_all("meta", attrs={"property": re.compile(r"^og:")})
    has_open_graph = len(og_tags) >= 2  # at minimum og:title + og:* something else

    # --- Schema.org markup (JSON-LD is by far the most common modern form) ---
    json_ld_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    has_microdata = bool(soup.find(attrs={"itemtype": re.compile(r"schema\.org")}))
    has_schema_markup = bool(json_ld_scripts) or has_microdata

    # --- Contact form ---
    forms = soup.find_all("form")
    has_contact_form = False
    for form in forms:
        form_text = form.get_text(" ", strip=True).lower()
        inputs = form.find_all(["input", "textarea"])
        input_types = {i.get("type", "text") for i in inputs}
        has_email_field = "email" in input_types or any(
            i.get("name", "").lower() in ("email", "your-email") for i in inputs
        )
        has_message_field = bool(form.find("textarea"))
        if has_email_field and has_message_field:
            has_contact_form = True
            break
        if "contact" in form_text and len(inputs) >= 2:
            has_contact_form = True
            break

    # --- WhatsApp click-to-chat button ---
    has_whatsapp_button = any(pattern in lower_html for pattern in WHATSAPP_PATTERNS)

    # --- Google Maps embed ---
    iframes = soup.find_all("iframe")
    has_google_maps_embed = any(
        iframe.get("src") and any(p in iframe["src"] for p in MAPS_EMBED_PATTERNS) for iframe in iframes
    )

    # --- Social links ---
    links = soup.find_all("a", href=True)
    found_socials = {
        domain for domain in SOCIAL_DOMAINS for link in links if domain in link["href"]
    }
    has_social_links = len(found_socials) > 0

    # --- Dark mode signal ---
    # Heuristic: prefers-color-scheme in inline/linked CSS, or a theme
    # toggle button with common naming, are the two realistic signals
    # without executing CSS ourselves.
    has_dark_mode = "prefers-color-scheme: dark" in lower_html or "dark-mode" in lower_html or "theme-toggle" in lower_html

    # --- Responsive design (viewport meta is the baseline signal) ---
    is_responsive = has_meta_viewport

    # --- Images for optimization scoring ---
    images = soup.find_all("img")
    images_missing_alt = sum(1 for img in images if not img.get("alt"))
    images_missing_dimensions = sum(1 for img in images if not (img.get("width") and img.get("height")))
    total_images = len(images)

    if total_images == 0:
        image_optimization_score = 100
    else:
        alt_ratio = 1 - (images_missing_alt / total_images)
        dim_ratio = 1 - (images_missing_dimensions / total_images)
        image_optimization_score = round(((alt_ratio + dim_ratio) / 2) * 100)

    # --- Links, for broken-link crawling by the caller ---
    same_domain_links = [link["href"] for link in links if link["href"].startswith(("/", base_url))]

    return {
        "has_favicon": has_favicon,
        "has_meta_tags": has_meta_tags,
        "has_open_graph": has_open_graph,
        "has_schema_markup": has_schema_markup,
        "has_contact_form": has_contact_form,
        "has_whatsapp_button": has_whatsapp_button,
        "has_google_maps_embed": has_google_maps_embed,
        "has_social_links": has_social_links,
        "has_dark_mode": has_dark_mode,
        "is_responsive": is_responsive,
        "image_optimization_score": image_optimization_score,
        "_same_domain_links": same_domain_links,  # internal use only, stripped before persisting
        "_found_social_domains": sorted(found_socials),  # internal, goes into raw_report
    }
