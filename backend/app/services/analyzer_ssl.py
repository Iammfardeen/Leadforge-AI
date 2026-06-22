"""
SSL/HTTPS validation.

Checks two distinct things, which the website_analyses table tracks
separately:
  - is_https: does the site's URL/redirect chain end up on https://?
  - has_ssl: is there a valid, non-expired SSL certificate on that connection?

A site can technically be "on https" with the browser still flagging the
cert as invalid (self-signed, expired, wrong hostname) — small business
sites hit this more often than you'd expect, especially expired certs on
abandoned WordPress installs.
"""
import socket
import ssl
from datetime import datetime, timezone
from urllib.parse import urlparse


def check_ssl(url: str, timeout: float = 8.0) -> dict:
    parsed = urlparse(url if "://" in url else f"https://{url}")
    hostname = parsed.hostname
    is_https = parsed.scheme == "https"

    if not hostname:
        return {"is_https": is_https, "has_ssl": False}

    if not is_https:
        # Still worth checking whether port 443 even has a usable cert,
        # in case the site silently supports https but isn't using it.
        port = 443
    else:
        port = parsed.port or 443

    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()

        not_after = cert.get("notAfter")
        if not_after:
            expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            has_ssl = expiry > datetime.now(timezone.utc)
        else:
            has_ssl = True  # connection + handshake succeeded, treat as valid

    except (socket.error, ssl.SSLError, socket.timeout, ConnectionRefusedError, OSError):
        has_ssl = False

    return {"is_https": is_https, "has_ssl": has_ssl}
