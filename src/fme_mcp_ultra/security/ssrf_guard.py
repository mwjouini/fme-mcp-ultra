"""SSRF Guard: Prevents Server-Side Request Forgery attacks."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse
from typing import List, Optional
from fme_mcp_ultra.core.config import settings
from fme_mcp_ultra.core.errors import SSRFError


class SSRFGuard:
    """Verifies URLs and resolves hostnames to disallow private and loopback networks."""

    def __init__(self, allowed_domains: Optional[List[str]] = None) -> None:
        self.allowed_domains = allowed_domains or settings.allowed_outbound_domains

    def validate_url(self, url: str) -> str:
        """Validate an outbound URL.

        Args:
            url: URL string to inspect.

        Returns:
            Sanitised URL.

        Raises:
            SSRFError: If the target resolves to a private, loopback, or metadata address.
        """
        if not url:
            raise SSRFError("Target URL cannot be empty")

        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise SSRFError(f"Unsupported URL scheme: {parsed.scheme}. Only HTTP/HTTPS permitted.")

        hostname = parsed.hostname
        if not hostname:
            raise SSRFError("Target URL missing valid hostname")

        # Resolve IP addresses for hostname
        try:
            addr_info = socket.getaddrinfo(hostname, None)
        except socket.gaierror as e:
            raise SSRFError(f"Failed to resolve hostname '{hostname}': {e}")

        for item in addr_info:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)

            # Block private, loopback, link-local, and reserved ranges
            if (
                ip_obj.is_private
                or ip_obj.is_loopback
                or ip_obj.is_link_local
                or ip_obj.is_reserved
                or ip_obj.is_multicast
            ):
                raise SSRFError(
                    f"Outbound connection to '{hostname}' ({ip_str}) blocked: private/loopback address."
                )

        return url


ssrf_guard = SSRFGuard()

