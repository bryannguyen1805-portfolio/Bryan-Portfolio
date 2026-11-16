#!/usr/bin/env python3
"""
secure_http_client.py — Bryan FinTech Intelligence Phase 05B-R1.3A.3
Secure HTTP Transport Layer with SSRF, DNS Pre-Resolution, Manual Redirect Protection,
and Measurement Source Document Validation.

Mandates:
1. HTTP and HTTPS schemes only (rejects file://, gopher://, etc.).
2. Hostname allowlist boundary validation.
3. Pre-resolution DNS checks: validates EVERY resolved A/AAAA record; blocks if ANY is restricted.
4. Manual redirect following: automatic redirects disabled.
5. Redirect destination validated BEFORE sending request to destination (Zero requests to prohibited destinations).
6. Enforces max redirect depth, timeout, and response size limits.
7. Preserves wire response bytes and computes deterministic SHA-256 hash.
8. Disqualifies homepages, category pages, and bot/cookie challenges from serving as measurement evidence.
"""

import os
import sys
import socket
import ipaddress
import hashlib
import gzip
from urllib.parse import urlparse, urljoin
import urllib.request
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone, timedelta
from typing import Tuple, List, Dict, Any, Optional

TIMEZONE_HCM = timezone(timedelta(hours=7))

# RFC 1918 & Restricted IPv4 and IPv6 Networks
RESTRICTED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),     # Loopback
    ipaddress.ip_network("10.0.0.0/8"),      # RFC 1918 Class A
    ipaddress.ip_network("172.16.0.0/12"),   # RFC 1918 Class B
    ipaddress.ip_network("192.168.0.0/16"),  # RFC 1918 Class C
    ipaddress.ip_network("169.254.0.0/16"),  # Link-Local & Cloud Metadata (169.254.169.254)
    ipaddress.ip_network("100.64.0.0/10"),   # Carrier-Grade NAT
    ipaddress.ip_network("224.0.0.0/4"),     # Multicast
    ipaddress.ip_network("0.0.0.0/8"),       # Zero network
    ipaddress.ip_network("::1/128"),         # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),        # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),       # IPv6 Link-Local
]

DEFAULT_TIMEOUT_SECONDS = 10
MAX_REDIRECT_HOPS = 3
MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB limit
USER_AGENT = "BryanFinTechIntelligence/3.0 (Operational Editorial Engine; +https://bryan-nguyen.com)"


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Disables automatic redirect handling so redirects can be inspected and validated manually."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class SecureHTTPClient:
    """Hardened HTTP Client enforcing zero-trust transport security, manual redirect inspection, and SSRF mitigation."""

    def __init__(self, test_mode: bool = False, pinned_dns_map: Optional[Dict[str, List[str]]] = None):
        self.test_mode = test_mode
        self.pinned_dns_map = pinned_dns_map or {}
        # Opener with automatic redirect disabled
        self._opener = build_opener(NoRedirectHandler())

    @classmethod
    def is_ip_restricted(cls, ip_str: str) -> bool:
        """Determines if an IPv4 or IPv6 address belongs to private, loopback, or cloud metadata ranges."""
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            return any(ip_obj in net for net in RESTRICTED_NETWORKS)
        except ValueError:
            return True

    def validate_destination_security(self, url: str, allowed_domains: list = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validates URL scheme, domain allowlist, and pre-resolves DNS to verify destination IP.
        Checks ALL resolved candidate IPs. Rejects if ANY candidate IP is restricted.
        Returns: (is_valid, error_reason, resolved_ip)
        """
        parsed = urlparse(url)
        scheme = parsed.scheme.lower()
        if scheme not in ("http", "https"):
            return False, f"PROHIBITED_SCHEME: Scheme '{scheme}' is prohibited. Only http/https allowed.", None

        hostname = parsed.hostname
        if not hostname:
            return False, "INVALID_URL: Missing hostname.", None

        # Test mode bypass for loopback mock test servers (127.0.0.1, localhost)
        if self.test_mode and hostname in ("127.0.0.1", "localhost", "::1"):
            return True, None, "127.0.0.1"

        # Domain allowlist check
        if allowed_domains:
            allowed = [d.lower() for d in allowed_domains]
            host_lower = hostname.lower()
            matched = any(host_lower == d or host_lower.endswith("." + d) for d in allowed)
            if not matched:
                return False, f"DOMAIN_NOT_ALLOWLISTED: Hostname '{hostname}' is not in approved indicator spec.", None

        # Pre-flight DNS resolution
        port = parsed.port or (443 if scheme == "https" else 80)
        try:
            if hostname in self.pinned_dns_map:
                candidate_ips = self.pinned_dns_map[hostname]
            else:
                addr_info = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
                candidate_ips = list({ai[4][0] for ai in addr_info})
        except socket.gaierror as e:
            return False, f"DNS_RESOLUTION_FAILURE: Cannot resolve hostname '{hostname}': {str(e)}", None

        if not candidate_ips:
            return False, f"DNS_EMPTY_RESOLUTION: No IP addresses resolved for hostname '{hostname}'", None

        # Test mode bypass for loopback mock test servers
        if self.test_mode and all(ip in ("127.0.0.1", "::1") for ip in candidate_ips):
            return True, None, "127.0.0.1"

        # Production SSRF IP filter: check EVERY resolved IP address
        for ip in candidate_ips:
            if self.is_ip_restricted(ip):
                return False, f"SSRF_BLOCKED: Hostname '{hostname}' resolves to restricted IP '{ip}' (Address prohibited)", None

        return True, None, candidate_ips[0]

    @classmethod
    def is_unusable_page_type(cls, url: str, content: str, status_code: int = 200) -> Tuple[bool, str]:
        """
        Enforces Section 3 of Master Execution Order:
        Homepages, category listing pages, and cookie/bot challenges must never
        qualify as financial measurement evidence.
        """
        if status_code in (403, 503):
            return True, f"HTTP_ERROR_RESPONSE: Server returned status {status_code}"

        lower_c = content.lower() if content else ""

        # Bot challenge / Captcha / Cloudflare / Fixture contamination check
        if any(marker in lower_c for marker in ["cf-challenge", "challenge-platform", "bot-detect", "just a moment...", "cookie challenge", "xác thực người dùng", "test_fixture_only"]):
            return True, "COOKIE_CHALLENGE_REJECTED: Bot challenge or test fixture cannot qualify as measurement evidence."

        parsed = urlparse(url)
        path = parsed.path.rstrip("/")

        # Homepage check
        if path in ("", "/vi/trang-chu", "/trang-chu", "/index.html", "/default.aspx", "/home", "/vi"):
            return True, "HOMEPAGE_REJECTED: Publisher homepage cannot qualify as measurement evidence."

        # Category / index page check (stream of links without an article body or focal data table)
        cat_markers = ["/category", "/chuyen-muc", "/danh-muc", "/tags/", "/tai-chinh.htm", "/tien-te-dau-tu", "/tai-chinh-ngan-hang.chn", "/thi-truong.htm"]
        is_cat_url = any(cm in path for cm in cat_markers) or path.endswith("/category")
        if is_cat_url:
            # Check if this is a listing page rather than a specific article or table
            has_article_body = any(tag in lower_c for tag in [
                "class=\"detail__content\"", "class=\"content-detail\"", "itemprop=\"articlebody\"",
                "<article", "class=\"article-content\"", "class=\"table-responsive\""
            ])
            if not has_article_body:
                return True, "CATEGORY_PAGE_REJECTED: Category listing page without focal article/table cannot qualify as measurement evidence."

        return False, "VALID_SOURCE_DOCUMENT"

    def get(self, target_url: str, allowed_domains: list = None, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
        """
        Executes a secure HTTP GET request with manual redirect following, boundary validation,
        and wire byte capture. Ensures destination receives ZERO requests if prohibited.
        """
        retrieved_at = datetime.now(TIMEZONE_HCM).isoformat()
        current_url = target_url
        redirect_chain = []
        hop_count = 0

        while hop_count <= MAX_REDIRECT_HOPS:
            # 1. Security validation on current URL before making connection
            is_valid, sec_err, resolved_ip = self.validate_destination_security(current_url, allowed_domains)
            if not is_valid:
                return {
                    "statusCode": 0,
                    "originalUrl": target_url,
                    "finalUrl": current_url,
                    "redirectChain": redirect_chain,
                    "retrievedAt": retrieved_at,
                    "byteLength": 0,
                    "responseSha256": None,
                    "originalBytes": b"",
                    "contentType": None,
                    "error": f"SECURITY_BLOCKED: {sec_err}"
                }

            # 2. Build HTTP Request
            req = Request(current_url, headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/json,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate"
            })

            try:
                # Open with NoRedirectHandler opener
                resp = self._opener.open(req, timeout=timeout)
                status_code = resp.status if hasattr(resp, 'status') else resp.getcode()
                content_type = resp.headers.get("Content-Type")

                # Read raw bytes with size limit
                raw_bytes = resp.read(MAX_RESPONSE_BYTES + 1)
                if len(raw_bytes) > MAX_RESPONSE_BYTES:
                    return {
                        "statusCode": 0,
                        "originalUrl": target_url,
                        "finalUrl": current_url,
                        "redirectChain": redirect_chain,
                        "retrievedAt": retrieved_at,
                        "byteLength": 0,
                        "responseSha256": None,
                        "originalBytes": b"",
                        "contentType": content_type,
                        "error": f"RESPONSE_TOO_LARGE: Response exceeded {MAX_RESPONSE_BYTES} bytes"
                    }

                # Wire SHA-256
                sha256 = hashlib.sha256(raw_bytes).hexdigest()

                return {
                    "statusCode": status_code,
                    "originalUrl": target_url,
                    "finalUrl": current_url,
                    "redirectChain": redirect_chain,
                    "retrievedAt": retrieved_at,
                    "byteLength": len(raw_bytes),
                    "responseSha256": sha256,
                    "originalBytes": raw_bytes,
                    "contentType": content_type,
                    "error": None
                }

            except HTTPError as e:
                # Check for redirect status codes (301, 302, 303, 307, 308)
                if e.code in (301, 302, 303, 307, 308):
                    hop_count += 1
                    if hop_count > MAX_REDIRECT_HOPS:
                        return {
                            "statusCode": 0,
                            "originalUrl": target_url,
                            "finalUrl": current_url,
                            "redirectChain": redirect_chain,
                            "retrievedAt": retrieved_at,
                            "byteLength": 0,
                            "responseSha256": None,
                            "originalBytes": b"",
                            "contentType": None,
                            "error": f"SECURITY_BLOCKED: Exceeded maximum redirect hops ({MAX_REDIRECT_HOPS})"
                        }

                    location = e.headers.get("Location")
                    if not location:
                        return {
                            "statusCode": 0,
                            "originalUrl": target_url,
                            "finalUrl": current_url,
                            "redirectChain": redirect_chain,
                            "retrievedAt": retrieved_at,
                            "byteLength": 0,
                            "responseSha256": None,
                            "originalBytes": b"",
                            "contentType": None,
                            "error": "INVALID_REDIRECT: Server returned redirect status without Location header"
                        }

                    next_url = urljoin(current_url, location)
                    redirect_chain.append({"from": current_url, "to": next_url, "status": e.code})

                    # CRITICAL: Validate destination before sending request
                    is_next_valid, next_sec_err, _ = self.validate_destination_security(next_url, allowed_domains)
                    if not is_next_valid:
                        return {
                            "statusCode": 0,
                            "originalUrl": target_url,
                            "finalUrl": next_url,
                            "redirectChain": redirect_chain,
                            "retrievedAt": retrieved_at,
                            "byteLength": 0,
                            "responseSha256": None,
                            "originalBytes": b"",
                            "contentType": None,
                            "error": f"SECURITY_BLOCKED: {next_sec_err}"
                        }

                    current_url = next_url
                    continue

                else:
                    # Non-redirect HTTP error (e.g. 404, 403, 500)
                    body_bytes = e.read() if hasattr(e, 'read') else b""
                    sha256 = hashlib.sha256(body_bytes).hexdigest() if body_bytes else None
                    return {
                        "statusCode": e.code,
                        "originalUrl": target_url,
                        "finalUrl": current_url,
                        "redirectChain": redirect_chain,
                        "retrievedAt": retrieved_at,
                        "byteLength": len(body_bytes),
                        "responseSha256": sha256,
                        "originalBytes": body_bytes,
                        "contentType": e.headers.get("Content-Type") if hasattr(e, 'headers') else None,
                        "error": f"HTTP_ERROR_{e.code}: {e.reason}"
                    }

            except (URLError, socket.timeout) as e:
                return {
                    "statusCode": 0,
                    "originalUrl": target_url,
                    "finalUrl": current_url,
                    "redirectChain": redirect_chain,
                    "retrievedAt": retrieved_at,
                    "byteLength": 0,
                    "responseSha256": None,
                    "originalBytes": b"",
                    "contentType": None,
                    "error": f"NETWORK_OR_URL_ERROR: {str(e)}"
                }
            except Exception as e:
                return {
                    "statusCode": 0,
                    "originalUrl": target_url,
                    "finalUrl": current_url,
                    "redirectChain": redirect_chain,
                    "retrievedAt": retrieved_at,
                    "byteLength": 0,
                    "responseSha256": None,
                    "originalBytes": b"",
                    "contentType": None,
                    "error": f"CLIENT_EXCEPTION: {str(e)}"
                }

        return {
            "statusCode": 0,
            "originalUrl": target_url,
            "finalUrl": current_url,
            "redirectChain": redirect_chain,
            "retrievedAt": retrieved_at,
            "byteLength": 0,
            "responseSha256": None,
            "originalBytes": b"",
            "contentType": None,
            "error": "MAX_REDIRECT_HOPS_EXCEEDED"
        }


# Backward-compatible alias
SecureHttpClient = SecureHTTPClient
