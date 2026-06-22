"""
Google Places integration for Lead Finder.

IMPORTANT — read before wiring this to production:

Google Places API (New) can reliably provide:
  - business name, formatted address, phone number (international format)
  - website URL (if the business listed one on their Google Business Profile)
  - rating, review count
  - place_id (used for de-duplication)
  - opening hours, business status (operational/closed)

Google Places CANNOT provide, and this service does NOT fabricate:
  - owner name              -> left null; would require a separate, manual,
                                or scraped source (e.g. public LinkedIn search),
                                which is unreliable and out of scope here
  - email address            -> left null; Places never returns this
  - Instagram / Facebook URL -> left null; would require scraping the
                                business's own website (see services/scraper.py
                                for a best-effort implementation you can enable)
  - business age             -> estimated heuristically from review patterns
                                if at all possible; otherwise null. Treat any
                                non-null value here as a rough guess, not fact.

This module requires the CALLER to supply their own Google Places API key
(stored per-user in user_settings.google_places_api_key) because:
  1. Places API has a monthly free credit, then bills per request.
  2. Sharing one key across all users of this app would blow through quota
     and tie billing to you instead of the end user.

If no key is configured, search_businesses raises a clear error rather than
silently returning mock data.
"""
import httpx

from app.core.config import get_settings

settings = get_settings()

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

FIELD_MASK = (
    "places.displayName,places.formattedAddress,places.internationalPhoneNumber,"
    "places.websiteUri,places.rating,places.userRatingCount,places.id,"
    "places.businessStatus,places.types"
)


class PlacesAPIError(Exception):
    pass


def search_businesses(city: str, category: str, max_results: int = 20, api_key: str | None = None) -> list[dict]:
    key = api_key or settings.GOOGLE_PLACES_API_KEY
    if not key:
        raise PlacesAPIError(
            "No Google Places API key configured. Add one in Settings -> API Keys "
            "to use Lead Finder. Get a free-tier key at "
            "https://developers.google.com/maps/documentation/places/web-service/get-api-key"
        )

    query = f"{category} in {city}"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body = {"textQuery": query, "maxResultCount": min(max_results, 20)}

    try:
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(PLACES_TEXT_SEARCH_URL, headers=headers, json=body)
    except httpx.HTTPError as exc:
        raise PlacesAPIError(f"Network error calling Google Places API: {exc}") from exc

    if resp.status_code != 200:
        raise PlacesAPIError(f"Google Places API error ({resp.status_code}): {resp.text}")

    data = resp.json()
    places = data.get("places", [])

    results = []
    for place in places:
        website = place.get("websiteUri")
        results.append(
            {
                "business_name": place.get("displayName", {}).get("text"),
                "owner_name": None,  # not available via Places API — see module docstring
                "phone": place.get("internationalPhoneNumber"),
                "email": None,  # not available via Places API
                "website_url": website,
                "google_rating": place.get("rating"),
                "review_count": place.get("userRatingCount"),
                "address": place.get("formattedAddress"),
                "city": city,
                "category": category,
                "business_age_years": None,  # not directly available; see docstring
                "has_website": bool(website),
                "instagram_url": None,  # would require scraping the business website
                "facebook_url": None,   # would require scraping the business website
                "google_place_id": place.get("id"),
            }
        )

    return results
