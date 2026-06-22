"""
Broken link checker.

Scope is intentionally narrow: same-domain links found on the homepage
only (depth 1), checked with HEAD requests (falling back to GET if a server
doesn't support HEAD, which a surprising number of small-business hosts
don't). This stays fast and avoids hammering a small business's server.

Capped at MAX_LINKS_TO_CHECK so a homepage with hundreds of links doesn't
turn an analysis run into a multi-minute operation.
"""
from urllib.parse import urljoin, urlparse

import httpx

MAX_LINKS_TO_CHECK = 25
REQUEST_TIMEOUT = 6.0


def count_broken_links(base_url: str, same_domain_links: list[str]) -> int:
    parsed_base = urlparse(base_url)
    seen: set[str] = set()
    to_check: list[str] = []

    for href in same_domain_links:
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        # Skip anchors, mailto:, tel:, javascript:, and cross-domain links
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.netloc and parsed.netloc != parsed_base.netloc:
            continue
        if not parsed.path or parsed.path == "/":
            continue  # homepage itself, not worth re-checking

        normalized = full_url.split("#")[0]
        if normalized in seen:
            continue
        seen.add(normalized)
        to_check.append(normalized)

        if len(to_check) >= MAX_LINKS_TO_CHECK:
            break

    broken_count = 0
    headers = {"User-Agent": "Mozilla/5.0 (compatible; LeadForgeBot/1.0; +website-audit)"}

    with httpx.Client(timeout=REQUEST_TIMEOUT, follow_redirects=True, headers=headers) as client:
        for link in to_check:
            try:
                resp = client.head(link)
                if resp.status_code >= 400:
                    # Some servers reject HEAD but accept GET — confirm before counting as broken
                    resp = client.get(link)
                if resp.status_code >= 400:
                    broken_count += 1
            except httpx.HTTPError:
                broken_count += 1

    return broken_count
