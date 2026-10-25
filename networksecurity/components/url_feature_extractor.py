"""
URL Feature Extraction Component for Network Security Phishing Detection.

This module extracts the 30 discrete engineered cybersecurity features defined in the
UCI Phishing Websites Dataset (Mohammad, Thabtah, McCluskey, 2012 / 2015).

Pipeline Architecture:
    URL Input -> Syntax & SSRF Validation -> Lexical Extraction -> DNS/TLS Probing
              -> Safe HTML Parsing -> Documented Heuristic Baseline -> 30-Feature Vector

Features Capability Map & Documentation:
-----------------------------------------
1. having_IP_Address:
   - Domain: {-1, 1} (-1: IP address used as hostname, 1: domain name used)
   - Source: URL String (Lexical)
   - Method: Parses hostname and checks for IPv4 (decimal, hex, octal) or IPv6 format.

2. URL_Length:
   - Domain: {-1, 0, 1} (1: < 54 chars, 0: 54-75 chars, -1: > 75 chars)
   - Source: URL String (Lexical)
   - Method: Measures string length of entire input URL.

3. Shortining_Service:
   - Domain: {-1, 1} (-1: uses known URL shortening service, 1: direct domain)
   - Source: URL String (Lexical)
   - Method: Compares hostname against curated registry of URL shorteners (bit.ly, tinyurl, etc.).

4. having_At_Symbol:
   - Domain: {-1, 1} (-1: contains '@' symbol, 1: no '@' symbol)
   - Source: URL String (Lexical)
   - Method: Checks presence of '@' character, which causes browsers to ignore preceding text.

5. double_slash_redirecting:
   - Domain: {-1, 1} (-1: '//' appears in URL path, 1: '//' only after protocol)
   - Source: URL String (Lexical)
   - Method: Checks if '//' occurs after position 7 in the URL string.

6. Prefix_Suffix:
   - Domain: {-1, 1} (-1: hyphen '-' in domain name, 1: no hyphen)
   - Source: URL String (Lexical)
   - Method: Inspects hostname labels for '-' symbol commonly used in brand spoofing.

7. having_Sub_Domain:
   - Domain: {-1, 0, 1} (1: 0-1 subdomains/dots, 0: 2 subdomains/dots, -1: > 2 subdomains)
   - Source: URL String (Lexical)
   - Method: Strips 'www' and counts remaining domain label separators.

8. SSLfinal_State:
   - Domain: {-1, 0, 1} (1: valid HTTPS with trusted CA, 0: untrusted/expired cert, -1: HTTP or SSL error)
   - Source: DNS/TLS Probing
   - Method: Performs TLS handshake, validates certificate chain, issuer, and expiration.

9. Domain_registeration_length:
   - Domain: {-1, 1} (-1: expires <= 1 year or unknown, 1: expires > 1 year)
   - Source: External WHOIS (Unavailable/Commercial)
   - Method: Documented heuristic fallback (-1: conservative assumption).

10. Favicon:
    - Domain: {-1, 1} (-1: favicon loaded from external domain, 1: loaded from same domain or relative)
    - Source: Safe HTML Content
    - Method: Inspects `<link rel="icon">` or `<link rel="shortcut icon">` tags.

11. port:
    - Domain: {-1, 1} (-1: non-standard port specified, 1: standard port 80/443/8080 or omitted)
    - Source: URL String (Lexical)
    - Method: Parses port from URL authority.

12. HTTPS_token:
    - Domain: {-1, 1} (-1: 'https' token inside hostname, 1: no 'https' in hostname)
    - Source: URL String (Lexical)
    - Method: Checks if 'https' appears inside hostname (e.g. http://https-secure-login.com).

13. Request_URL:
    - Domain: {-1, 1} (-1: >= 61% foreign media resources, 1: < 61% foreign)
    - Source: Safe HTML Content
    - Method: Calculates percentage of external domain `src` links in `<img>`, `<video>`, `<audio>`.

14. URL_of_Anchor:
    - Domain: {-1, 0, 1} (-1: > 67% foreign/empty anchors, 0: 31%-67%, 1: < 31%)
    - Source: Safe HTML Content
    - Method: Calculates percentage of `<a>` tags with `#`, `javascript:`, empty, or foreign domains.

15. Links_in_tags:
    - Domain: {-1, 0, 1} (-1: > 81% foreign links, 0: 17%-81%, 1: < 17%)
    - Source: Safe HTML Content
    - Method: Analyzes `<meta>`, `<script>`, `<link>` external domain ratio.

16. SFH (Server Form Handler):
    - Domain: {-1, 0, 1} (-1: form action empty or 'about:blank', 0: foreign domain, 1: same domain)
    - Source: Safe HTML Content
    - Method: Inspects `<form action="...">` attributes.

17. Submitting_to_email:
    - Domain: {-1, 1} (-1: form action or handler uses 'mailto:', 1: no mailto)
    - Source: Safe HTML Content / URL String
    - Method: Searches for 'mailto:' protocol handler in forms and links.

18. Abnormal_URL:
    - Domain: {-1, 1} (-1: hostname not part of URL path identity, 1: normal)
    - Source: URL String (Lexical)
    - Method: Validates host consistency against URL identity.

19. Redirect:
    - Domain: {0, 1} (0: > 1 redirect [phishing in schema], 1: <= 1 redirect [legitimate in schema])
    - Source: Network HTTP Response
    - Method: Counts HTTP 3xx redirect hops during safe fetch.

20. on_mouseover:
    - Domain: {-1, 1} (-1: JavaScript modifies window.status, 1: clean)
    - Source: Safe HTML Content
    - Method: Inspects HTML/JS for `window.status` manipulation.

21. RightClick:
    - Domain: {-1, 1} (-1: right click disabled by script, 1: clean)
    - Source: Safe HTML Content
    - Method: Inspects scripts for `event.button==2` or `contextmenu` prevention.

22. popUpWidnow:
    - Domain: {-1, 1} (-1: contains popup credential dialogs, 1: clean)
    - Source: Safe HTML Content
    - Method: Searches for `window.open` popup prompt patterns.

23. Iframe:
    - Domain: {-1, 1} (-1: invisible iframe with border 0 or hidden styling, 1: clean)
    - Source: Safe HTML Content
    - Method: Searches for `<iframe>` tags with `frameborder="0"` or hidden styling.

24. age_of_domain:
    - Domain: {-1, 1} (-1: domain age < 6 months or unknown, 1: >= 6 months)
    - Source: External WHOIS (Unavailable/Commercial)
    - Method: Documented heuristic fallback (1 if active TLS/DNS, else -1).

25. DNSRecord:
    - Domain: {-1, 1} (-1: no DNS record / resolution fails, 1: valid DNS A/AAAA record)
    - Source: DNS/TLS Probing
    - Method: Resolves domain using `socket.getaddrinfo`.

26. web_traffic:
    - Domain: {-1, 0, 1} (-1: no traffic rank / > 100k, 0: moderate, 1: top 100k)
    - Source: Alexa Traffic Rank (Service Officially Sunset in May 2022)
    - Method: Documented heuristic fallback (-1: conservative default).

27. Page_Rank:
    - Domain: {-1, 1} (-1: PageRank < 0.2 or unavailable, 1: >= 0.2)
    - Source: Google PageRank API (Service Officially Sunset in April 2016)
    - Method: Documented heuristic fallback (-1: conservative default).

28. Google_Index:
    - Domain: {-1, 1} (-1: not indexed, 1: indexed in search)
    - Source: Search Engine Indexing (Proprietary / Scraping Prohibited)
    - Method: Documented heuristic fallback (1 if live publicly accessible site, else -1).

29. Links_pointing_to_page:
    - Domain: {-1, 0, 1} (-1: 0 inbound links, 0: 1-2 links, 1: > 2 links)
    - Source: Backlink Intelligence (Commercial API)
    - Method: Documented heuristic fallback (0: neutral unknown).

30. Statistical_report:
    - Domain: {-1, 1} (-1: listed in PhishTank/StopBadware blacklist, 1: clean)
    - Source: Threat Intelligence Feed
    - Method: Documented heuristic fallback (1: clean default if not flagged).
"""

import datetime
import gzip
import html.parser
import http.client
import ipaddress
import os
import re
import socket
import ssl
import sys
import urllib.parse
import zlib
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.utils.ml_utils.model.estimator import EXPECTED_FEATURES

# Known URL Shortening Services
KNOWN_SHORTENERS: Set[str] = {
    "bit.ly", "goo.gl", "tinyurl.com", "ow.ly", "t.co", "is.gd", "buff.ly",
    "adf.ly", "bit.do", "rebrand.ly", "cutt.ly", "tiny.cc", "lnkd.in", "db.tt",
    "qr.ae", "curt.ly", "shorte.st", "trib.al", "bc.vc", "po.st", "v.gd"
}

# Standard HTTP/HTTPS ports
STANDARD_PORTS: Set[int] = {80, 443, 8080}

# Private / Prohibited IP Networks for SSRF Prevention
PROHIBITED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local / Cloud Metadata
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.0.0.0/24"),
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("192.88.99.0/24"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("198.18.0.0/15"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("224.0.0.0/4"),          # Multicast
    ipaddress.ip_network("240.0.0.0/4"),          # Reserved
    ipaddress.ip_network("255.255.255.255/32"),
    ipaddress.ip_network("::/128"),
    ipaddress.ip_network("::1/128"),              # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),             # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),            # IPv6 link-local
]

# Capability categorization
STAGE_URL_LEXICAL = [
    "having_IP_Address", "URL_Length", "Shortining_Service", "having_At_Symbol",
    "double_slash_redirecting", "Prefix_Suffix", "having_Sub_Domain", "port",
    "HTTPS_token", "Abnormal_URL"
]

STAGE_DNS_TLS = [
    "SSLfinal_State", "DNSRecord"
]

STAGE_HTML_CONTENT = [
    "Favicon", "Request_URL", "URL_of_Anchor", "Links_in_tags", "SFH",
    "Submitting_to_email", "Redirect", "on_mouseover", "RightClick",
    "popUpWidnow", "Iframe"
]

STAGE_EXTERNAL_INTEL = [
    "Domain_registeration_length", "age_of_domain", "web_traffic",
    "Page_Rank", "Google_Index", "Links_pointing_to_page", "Statistical_report"
]


class FeatureStatus:
    OBSERVED = "observed"
    EXTERNALLY_VERIFIED = "externally_verified"
    ESTIMATED = "estimated"
    MISSING = "missing"


class SSRFSecurityViolation(ValueError):
    """Raised when a URL attempts to target private, loopback, or reserved destinations."""
    pass


class InvalidURLFormatError(ValueError):
    """Raised when an input URL is malformed or uses unsupported schemes."""
    pass


def is_private_or_reserved_ip(ip_str: str) -> Tuple[bool, str]:
    """
    Validates whether an IP address belongs to private, loopback, link-local, or reserved blocks.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        # Check IPv4 mapped IPv6
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            ip = ip.ipv4_mapped

        if ip.is_private:
            return True, f"Private address space ({ip_str})"
        if ip.is_loopback:
            return True, f"Loopback address ({ip_str})"
        if ip.is_link_local:
            return True, f"Link-local / Cloud metadata address ({ip_str})"
        if ip.is_multicast:
            return True, f"Multicast address ({ip_str})"
        if ip.is_reserved:
            return True, f"Reserved address ({ip_str})"
        if ip.is_unspecified:
            return True, f"Unspecified address ({ip_str})"

        for net in PROHIBITED_NETWORKS:
            if ip in net:
                return True, f"Prohibited network block {net} ({ip_str})"

        return False, "Public IP"
    except ValueError:
        return True, f"Invalid IP format: {ip_str}"


def validate_and_sanitize_url(url: str, enforce_public_dns: bool = True) -> Dict[str, Any]:
    """
    Parses, validates, and screens a submitted URL against SSRF and malformed syntax.
    Returns parsed URL metadata dictionary.
    """
    if not isinstance(url, str) or not url.strip():
        raise InvalidURLFormatError("URL input cannot be empty.")

    clean_url = url.strip()

    # Reject URLs with embedded credentials (e.g. http://user:pass@host)
    if "@" in clean_url.split("/")[2] if len(clean_url.split("/")) > 2 else False:
        raise SSRFSecurityViolation("URLs with embedded user credentials (user:pass@) are prohibited.")

    try:
        parsed = urllib.parse.urlsplit(clean_url)
    except Exception as e:
        raise InvalidURLFormatError(f"Malformed URL structure: {e}")

    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        raise InvalidURLFormatError(
            f"Unsupported scheme '{scheme}'. Only standard 'http' and 'https' protocols are supported."
        )

    if not parsed.hostname:
        raise InvalidURLFormatError("URL must include a valid hostname.")

    hostname = parsed.hostname.lower()

    # Reject localhost domain names explicitly
    if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local") or hostname.endswith(".internal"):
        raise SSRFSecurityViolation(f"Host '{hostname}' references a local or internal domain name.")

    port = parsed.port or (443 if scheme == "https" else 80)
    if not (1 <= port <= 65535):
        raise InvalidURLFormatError(f"Port {port} is out of valid range (1-65535).")

    # SSRF Resolution Screening
    resolved_ips = []
    if enforce_public_dns:
        try:
            addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
            for item in addr_info:
                ip_str = item[4][0]
                is_prohibited, reason = is_private_or_reserved_ip(ip_str)
                if is_prohibited:
                    raise SSRFSecurityViolation(
                        f"SSRF violation: Host '{hostname}' resolves to prohibited {reason}."
                    )
                resolved_ips.append(ip_str)
        except socket.gaierror:
            # Domain does not resolve; allowed to proceed for offline/lexical tests
            pass

    return {
        "url": clean_url,
        "scheme": scheme,
        "hostname": hostname,
        "port": port,
        "path": parsed.path or "/",
        "query": parsed.query,
        "parsed": parsed,
        "resolved_ips": resolved_ips,
    }


class SimpleHTMLFeatureParser(html.parser.HTMLParser):
    """
    Lightweight, streaming HTML feature extractor using Python standard library.
    Executes no scripts, renders no content, and enforces strict memory limits.
    """
    def __init__(self, base_url: str, base_hostname: str):
        super().__init__()
        self.base_url = base_url
        self.base_hostname = base_hostname

        self.favicons: List[str] = []
        self.media_srcs: List[str] = []
        self.anchor_hrefs: List[str] = []
        self.tag_links: List[str] = []
        self.form_actions: List[str] = []
        self.has_mailto: bool = False
        self.has_window_status: bool = False
        self.has_disabled_rightclick: bool = False
        self.has_popup_prompt: bool = False
        self.has_hidden_iframe: bool = False
        self.has_password_field: bool = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()

        # Favicon
        if tag == "link":
            rel = attr_dict.get("rel", "").lower()
            if "icon" in rel or "shortcut icon" in rel:
                href = attr_dict.get("href", "")
                if href:
                    self.favicons.append(href)
            href = attr_dict.get("href", "")
            if href:
                self.tag_links.append(href)

        # Media Request URLs
        if tag in ("img", "video", "audio", "embed"):
            src = attr_dict.get("src", "")
            if src:
                self.media_srcs.append(src)

        # Anchor URLs
        if tag == "a":
            href = attr_dict.get("href", "")
            self.anchor_hrefs.append(href)
            if href.lower().startswith("mailto:"):
                self.has_mailto = True

        # Tag links: script, meta
        if tag == "script":
            src = attr_dict.get("src", "")
            if src:
                self.tag_links.append(src)

        # Server Form Handler (SFH)
        if tag == "form":
            action = attr_dict.get("action", "")
            self.form_actions.append(action)
            if action.lower().startswith("mailto:"):
                self.has_mailto = True

        # Iframe
        if tag == "iframe":
            frameborder = attr_dict.get("frameborder", "")
            style = attr_dict.get("style", "").replace(" ", "").lower()
            width = attr_dict.get("width", "")
            height = attr_dict.get("height", "")

            if frameborder == "0" or "display:none" in style or "visibility:hidden" in style or width in ("0", "0px") or height in ("0", "0px"):
                self.has_hidden_iframe = True

        # Input password fields (credential forms)
        if tag == "input":
            input_type = attr_dict.get("type", "").lower()
            input_name = attr_dict.get("name", "").lower()
            if input_type == "password" or "password" in input_name or "passwd" in input_name:
                self.has_password_field = True

        # Check inline JS attributes
        for k, v in attr_dict.items():
            val = v.lower()
            if "window.status" in val:
                self.has_window_status = True
            if "event.button==2" in val or "event.button == 2" in val or "contextmenu" in k:
                self.has_disabled_rightclick = True
            if "prompt(" in val or "window.open(" in val:
                self.has_popup_prompt = True

    def handle_data(self, data: str):
        content = data.lower()
        if "window.status" in content:
            self.has_window_status = True
        if "event.button==2" in content or "event.button == 2" in content or "oncontextmenu" in content:
            self.has_disabled_rightclick = True
        if "prompt(" in content:
            self.has_popup_prompt = True


class URLFeatureExtractor:
    """
    Dedicated URL feature extractor implementing the exact 30-feature schema.
    """

    def __init__(self, timeout: float = 3.0, max_content_bytes: int = 524288):
        self.timeout = timeout
        self.max_content_bytes = max_content_bytes

    def extract_lexical_features(self, url: str, parsed: urllib.parse.SplitResult) -> Dict[str, int]:
        """
        Extracts all 10 URL string (lexical) features.
        """
        features: Dict[str, int] = {}
        hostname = (parsed.hostname or "").lower()

        # 1. having_IP_Address: -1 if IP, 1 if domain
        is_ip = False
        try:
            ipaddress.ip_address(hostname)
            is_ip = True
        except ValueError:
            # Also check hex or octal IP patterns
            if re.match(r"^0x[0-9a-fA-F]+\.[0-9a-fA-F\.]+$", hostname) or re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", hostname):
                is_ip = True
        features["having_IP_Address"] = -1 if is_ip else 1

        # 2. URL_Length: <54 -> 1, 54..75 -> 0, >75 -> -1
        u_len = len(url)
        if u_len < 54:
            features["URL_Length"] = 1
        elif 54 <= u_len <= 75:
            features["URL_Length"] = 0
        else:
            features["URL_Length"] = -1

        # 3. Shortining_Service: -1 if shortened, 1 if direct
        is_short = False
        host_parts = hostname.split(".")
        if len(host_parts) >= 2:
            main_domain = ".".join(host_parts[-2:])
            if hostname in KNOWN_SHORTENERS or main_domain in KNOWN_SHORTENERS:
                is_short = True
        features["Shortining_Service"] = -1 if is_short else 1

        # 4. having_At_Symbol: -1 if '@', 1 if none
        features["having_At_Symbol"] = -1 if "@" in url else 1

        # 5. double_slash_redirecting: -1 if '//' in path, 1 if clean
        # Find position of last '//' in the entire URL
        last_double_slash = url.rfind("//")
        features["double_slash_redirecting"] = -1 if last_double_slash > 7 else 1

        # 6. Prefix_Suffix: -1 if '-' in hostname, 1 if clean
        features["Prefix_Suffix"] = -1 if "-" in hostname else 1

        # 7. having_Sub_Domain: dots in hostname (minus www)
        # 1 dot -> 1, 2 dots -> 0, >2 dots -> -1
        clean_host = hostname
        if clean_host.startswith("www."):
            clean_host = clean_host[4:]
        dots = clean_host.count(".")
        if dots <= 1:
            features["having_Sub_Domain"] = 1
        elif dots == 2:
            features["having_Sub_Domain"] = 0
        else:
            features["having_Sub_Domain"] = -1

        # 11. port: -1 if non-standard, 1 if standard
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        features["port"] = 1 if port in STANDARD_PORTS else -1

        # 12. HTTPS_token: -1 if 'https' inside hostname, 1 if clean
        features["HTTPS_token"] = -1 if "https" in hostname else 1

        # 18. Abnormal_URL: -1 if host identity is abnormal/missing, 1 if clean
        features["Abnormal_URL"] = 1 if hostname and ("." in hostname or is_ip) else -1

        return features

    def extract_dns_tls_features(self, hostname: str, scheme: str, port: int) -> Dict[str, int]:
        """
        Extracts DNS resolution and TLS certificate state.
        """
        features: Dict[str, int] = {}

        # 25. DNSRecord: 1 if resolved, -1 if resolution failed
        has_dns = False
        try:
            addr_info = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
            if addr_info and len(addr_info) > 0:
                has_dns = True
        except (socket.gaierror, socket.herror, TimeoutError):
            has_dns = False
        features["DNSRecord"] = 1 if has_dns else -1

        # 8. SSLfinal_State: 1 if valid HTTPS + trusted cert, 0 if untrusted/expired/short-lived, -1 if HTTP or error
        if scheme.lower() != "https":
            features["SSLfinal_State"] = -1
        else:
            ssl_state = -1
            try:
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()
                        if cert:
                            # Verify validity duration (>= 1 year is legitimate)
                            not_after_str = cert.get("notAfter")
                            not_before_str = cert.get("notBefore")
                            if not_after_str and not_before_str:
                                not_after = datetime.datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z")
                                not_before = datetime.datetime.strptime(not_before_str, "%b %d %H:%M:%S %Y %Z")
                                validity_days = (not_after - not_before).days
                                # Modern TLS standards (Let's Encrypt / DigiCert) issue 90-day certificates
                                ssl_state = 1 if validity_days >= 80 else 0
                            else:
                                ssl_state = 1
            except ssl.SSLCertVerificationError:
                ssl_state = 0  # Untrusted or expired certificate
            except Exception:
                ssl_state = -1  # TLS connection failed entirely
            features["SSLfinal_State"] = ssl_state

        return features

    def safe_fetch_page(self, url: str, base_hostname: str) -> Tuple[Optional[str], int, Optional[str]]:
        """
        Safely fetches page HTML with strict SSRF checks, redirect limits, and size caps.
        Returns (html_string, redirect_count, error_message).
        """
        current_url = url
        redirect_count = 0
        max_redirects = 2

        for _ in range(max_redirects + 1):
            try:
                # SSRF validation of current URL
                url_meta = validate_and_sanitize_url(current_url, enforce_public_dns=True)
            except (SSRFSecurityViolation, InvalidURLFormatError) as e:
                return None, redirect_count, str(e)

            parsed = url_meta["parsed"]
            host = url_meta["hostname"]
            port = url_meta["port"]
            scheme = url_meta["scheme"]
            path = parsed.path or "/"
            if parsed.query:
                path = f"{path}?{parsed.query}"

            try:
                if scheme == "https":
                    context = ssl.create_default_context()
                    conn = http.client.HTTPSConnection(host, port=port, timeout=self.timeout, context=context)
                else:
                    conn = http.client.HTTPConnection(host, port=port, timeout=self.timeout)

                headers = {
                    "User-Agent": "PhishGuard-Security-Auditor/1.0 (+https://github.com/rahul15-manch/networksecurity)",
                    "Accept": "text/html,application/xhtml+xml;q=0.9",
                    "Connection": "close",
                }

                conn.request("GET", path, headers=headers)
                response = conn.getresponse()

                # Handle HTTP redirects
                if response.status in (301, 302, 303, 307, 308):
                    redirect_count += 1
                    location = response.getheader("Location")
                    if not location or redirect_count > max_redirects:
                        return None, redirect_count, "Too many redirects or missing Location header."
                    # Resolve relative redirect
                    current_url = urllib.parse.urljoin(current_url, location)
                    conn.close()
                    continue

                if response.status >= 400:
                    conn.close()
                    return None, redirect_count, f"HTTP server returned status {response.status}."

                content_type = response.getheader("Content-Type", "").lower()
                if "text/html" not in content_type and "application/xhtml" not in content_type:
                    # Not an HTML page
                    conn.close()
                    return None, redirect_count, f"Unsupported response Content-Type: {content_type}"

                # Read body with max byte limit
                body_bytes = response.read(self.max_content_bytes + 1)
                conn.close()

                if len(body_bytes) > self.max_content_bytes:
                    body_bytes = body_bytes[:self.max_content_bytes]

                # Decompress HTTP payload if Content-Encoding is gzip or deflate
                content_encoding = response.getheader("Content-Encoding", "").lower()
                if "gzip" in content_encoding or body_bytes[:2] == b"\x1f\x8b":
                    try:
                        body_bytes = gzip.decompress(body_bytes)
                    except Exception as e:
                        logging.warning(f"Failed to decompress gzip content: {e}")
                elif "deflate" in content_encoding or (len(body_bytes) > 2 and body_bytes[:2] in (b"\x78\x9c", b"\x78\x01", b"\x78\xda")):
                    try:
                        body_bytes = zlib.decompress(body_bytes)
                    except Exception as e:
                        logging.warning(f"Failed to decompress deflate content: {e}")

                html_text = body_bytes.decode("utf-8", errors="replace")
                return html_text, redirect_count, None

            except Exception as e:
                return None, redirect_count, f"Network connection failed: {e}"

        return None, redirect_count, "Exceeded maximum redirect depth."

    def extract_html_features(
        self,
        html_content: Optional[str],
        base_hostname: str,
        redirect_count: int = 0,
        allow_heuristics: bool = False,
    ) -> Tuple[Dict[str, Optional[int]], Dict[str, Dict[str, Any]]]:
        """
        Extracts 11 HTML/content features from safely parsed HTML.
        Returns (features_dict, details_dict).
        Replaces optimistic defaults with evidence-based status tracking.
        """
        features: Dict[str, Optional[int]] = {}
        details: Dict[str, Dict[str, Any]] = {}

        # 19. Redirect: 0 (>1 redirects, phishing in schema), 1 (<=1 redirect, legitimate in schema)
        redir_val = 1 if redirect_count <= 1 else 0
        features["Redirect"] = redir_val
        details["Redirect"] = {
            "name": "Redirect",
            "value": redir_val,
            "status": FeatureStatus.OBSERVED,
            "evidence_source": "http_network",
            "explanation": f"Observed {redirect_count} HTTP redirect(s)",
        }

        html_dom_keys = [
            "Favicon", "Request_URL", "URL_of_Anchor", "Links_in_tags", "SFH",
            "Submitting_to_email", "on_mouseover", "RightClick", "popUpWidnow", "Iframe"
        ]

        if not html_content or not html_content.strip():
            # HTML unavailable (server offline, non-HTML, or offline mode)
            for k in html_dom_keys:
                if allow_heuristics:
                    val = 0 if k in ("Favicon", "Request_URL", "URL_of_Anchor", "Links_in_tags", "SFH") else 1
                    features[k] = val
                    details[k] = {
                        "name": k,
                        "value": val,
                        "status": FeatureStatus.ESTIMATED,
                        "evidence_source": "heuristic_baseline",
                        "explanation": "HTML content could not be retrieved; neutral baseline applied",
                    }
                else:
                    features[k] = None
                    details[k] = {
                        "name": k,
                        "value": None,
                        "status": FeatureStatus.MISSING,
                        "evidence_source": "none",
                        "explanation": "HTML content unavailable; feature cannot be observed in strict mode",
                    }
            return features, details

        parser = SimpleHTMLFeatureParser(base_url=f"http://{base_hostname}", base_hostname=base_hostname)
        try:
            parser.feed(html_content)
        except Exception:
            pass

        def is_foreign_domain(link: str) -> bool:
            if not link or link.startswith("#") or link.lower().startswith("javascript:"):
                return False
            try:
                p = urllib.parse.urlsplit(link)
                if not p.hostname:
                    return False
                return p.hostname.lower() != base_hostname
            except Exception:
                return False

        # 10. Favicon
        if parser.favicons:
            fav_foreign = any(is_foreign_domain(fav) for fav in parser.favicons)
            fav_val = -1 if fav_foreign else 1
            features["Favicon"] = fav_val
            details["Favicon"] = {
                "name": "Favicon",
                "value": fav_val,
                "status": FeatureStatus.OBSERVED,
                "evidence_source": "html_dom",
                "explanation": "Favicon loaded from external foreign domain" if fav_foreign else "Favicon loaded from same domain or relative path",
            }
        else:
            features["Favicon"] = 0
            details["Favicon"] = {
                "name": "Favicon",
                "value": 0,
                "status": FeatureStatus.ESTIMATED,
                "evidence_source": "heuristic_baseline",
                "explanation": "No favicon link tag declared on page; neutral baseline applied",
            }

        # 13. Request_URL
        total_media = len(parser.media_srcs)
        if total_media > 0:
            foreign_media = sum(1 for src in parser.media_srcs if is_foreign_domain(src))
            media_ratio = (foreign_media / total_media) * 100.0
            req_val = -1 if media_ratio >= 61.0 else 1
            features["Request_URL"] = req_val
            details["Request_URL"] = {
                "name": "Request_URL",
                "value": req_val,
                "status": FeatureStatus.OBSERVED,
                "evidence_source": "html_dom",
                "explanation": f"Embedded media evaluated: {media_ratio:.1f}% foreign sources ({foreign_media}/{total_media})",
            }
        else:
            features["Request_URL"] = 0
            details["Request_URL"] = {
                "name": "Request_URL",
                "value": 0,
                "status": FeatureStatus.ESTIMATED,
                "evidence_source": "heuristic_baseline",
                "explanation": "No embedded media elements (img/video/audio) found on page; neutral baseline applied",
            }

        # 14. URL_of_Anchor
        total_anchors = len(parser.anchor_hrefs)
        if total_anchors > 0:
            suspicious_anchors = 0
            for href in parser.anchor_hrefs:
                h = href.strip().lower()
                if not h or h == "#" or h.startswith("javascript:") or is_foreign_domain(h):
                    suspicious_anchors += 1
            anchor_ratio = (suspicious_anchors / total_anchors) * 100.0
            if anchor_ratio > 67.0:
                anc_val = -1
            elif 31.0 <= anchor_ratio <= 67.0:
                anc_val = 0
            else:
                anc_val = 1
            features["URL_of_Anchor"] = anc_val
            details["URL_of_Anchor"] = {
                "name": "URL_of_Anchor",
                "value": anc_val,
                "status": FeatureStatus.OBSERVED,
                "evidence_source": "html_dom",
                "explanation": f"Anchor links evaluated: {anchor_ratio:.1f}% suspicious or foreign ({suspicious_anchors}/{total_anchors})",
            }
        else:
            features["URL_of_Anchor"] = 0
            details["URL_of_Anchor"] = {
                "name": "URL_of_Anchor",
                "value": 0,
                "status": FeatureStatus.ESTIMATED,
                "evidence_source": "heuristic_baseline",
                "explanation": "No anchor links found on page; neutral baseline applied (not assumed safe)",
            }

        # 15. Links_in_tags
        total_tags = len(parser.tag_links)
        if total_tags > 0:
            foreign_tags = sum(1 for lk in parser.tag_links if is_foreign_domain(lk))
            tag_ratio = (foreign_tags / total_tags) * 100.0
            if tag_ratio > 81.0:
                tag_val = -1
            elif 17.0 <= tag_ratio <= 81.0:
                tag_val = 0
            else:
                tag_val = 1
            features["Links_in_tags"] = tag_val
            details["Links_in_tags"] = {
                "name": "Links_in_tags",
                "value": tag_val,
                "status": FeatureStatus.OBSERVED,
                "evidence_source": "html_dom",
                "explanation": f"Tag links (script/link) evaluated: {tag_ratio:.1f}% foreign ({foreign_tags}/{total_tags})",
            }
        else:
            features["Links_in_tags"] = 0
            details["Links_in_tags"] = {
                "name": "Links_in_tags",
                "value": 0,
                "status": FeatureStatus.ESTIMATED,
                "evidence_source": "heuristic_baseline",
                "explanation": "No script/link tags found on page; neutral baseline applied",
            }

        # 16. SFH
        if parser.form_actions:
            has_blank_sfh = any(not a.strip() or a.strip().lower() == "about:blank" for a in parser.form_actions)
            has_foreign_sfh = any(is_foreign_domain(a) for a in parser.form_actions)
            if has_blank_sfh:
                sfh_val = -1
                expl = "Form action is empty or about:blank (phishing indicator)"
            elif has_foreign_sfh:
                sfh_val = 0
                expl = "Form action submits to foreign domain (suspicious)"
            else:
                sfh_val = 1
                expl = "Form action submits to same domain or relative path"
            features["SFH"] = sfh_val
            details["SFH"] = {
                "name": "SFH",
                "value": sfh_val,
                "status": FeatureStatus.OBSERVED,
                "evidence_source": "html_dom",
                "explanation": expl,
            }
        elif parser.has_password_field:
            features["SFH"] = -1
            details["SFH"] = {
                "name": "SFH",
                "value": -1,
                "status": FeatureStatus.OBSERVED,
                "evidence_source": "html_dom",
                "explanation": "Password credential input field present without declaring a server form handler (phishing indicator)",
            }
        else:
            features["SFH"] = 0
            details["SFH"] = {
                "name": "SFH",
                "value": 0,
                "status": FeatureStatus.ESTIMATED,
                "evidence_source": "heuristic_baseline",
                "explanation": "No form elements on page; neutral baseline applied",
            }

        # 17. Submitting_to_email
        email_val = -1 if parser.has_mailto else 1
        features["Submitting_to_email"] = email_val
        details["Submitting_to_email"] = {
            "name": "Submitting_to_email",
            "value": email_val,
            "status": FeatureStatus.OBSERVED,
            "evidence_source": "html_dom",
            "explanation": "Detected mailto: action in form or link" if parser.has_mailto else "No mailto: submission found in page content",
        }

        # 20. on_mouseover
        mo_val = -1 if parser.has_window_status else 1
        features["on_mouseover"] = mo_val
        details["on_mouseover"] = {
            "name": "on_mouseover",
            "value": mo_val,
            "status": FeatureStatus.OBSERVED,
            "evidence_source": "html_dom",
            "explanation": "Detected window.status manipulation on mouseover" if parser.has_window_status else "No window.status manipulation detected",
        }

        # 21. RightClick
        rc_val = -1 if parser.has_disabled_rightclick else 1
        features["RightClick"] = rc_val
        details["RightClick"] = {
            "name": "RightClick",
            "value": rc_val,
            "status": FeatureStatus.OBSERVED,
            "evidence_source": "html_dom",
            "explanation": "Detected right-click context menu disabling" if parser.has_disabled_rightclick else "Right-click context menu operates normally",
        }

        # 22. popUpWidnow
        pop_val = -1 if parser.has_popup_prompt else 1
        features["popUpWidnow"] = pop_val
        details["popUpWidnow"] = {
            "name": "popUpWidnow",
            "value": pop_val,
            "status": FeatureStatus.OBSERVED,
            "evidence_source": "html_dom",
            "explanation": "Detected prompt() or popup prompt window in script" if parser.has_popup_prompt else "No modal prompt window detected",
        }

        # 23. Iframe
        if_val = -1 if parser.has_hidden_iframe else 1
        features["Iframe"] = if_val
        details["Iframe"] = {
            "name": "Iframe",
            "value": if_val,
            "status": FeatureStatus.OBSERVED,
            "evidence_source": "html_dom",
            "explanation": "Detected invisible or hidden iframe element" if parser.has_hidden_iframe else "No hidden iframes detected",
        }

        return features, details

    def get_documented_heuristic_features(self, is_accessible: bool = True) -> Dict[str, int]:
        """
        Supplies documented, evidence-based neutral baselines for external/retired services
        (Alexa Rank, Google PageRank, WHOIS). Replaces optimistic defaults with neutral values.
        """
        return {
            "Domain_registeration_length": -1,  # Conservative WHOIS baseline (<= 1 year)
            "age_of_domain": 0,                # Neutral domain age (not assumed mature)
            "web_traffic": 0,                  # Neutral rank tier (Alexa API retired May 2022)
            "Page_Rank": -1,                   # Low PageRank baseline (Google PageRank API retired April 2016)
            "Google_Index": 0,                 # Neutral search index status (not assumed indexed)
            "Links_pointing_to_page": 0,       # Neutral backlink count baseline
            "Statistical_report": 0,           # Neutral threat intelligence (not assumed clean)
        }

    def extract_features(
        self,
        url: str,
        allow_heuristics: bool = False,
        fetch_network: bool = True,
        mock_html: Optional[str] = None,
        mock_dns: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Executes complete feature extraction pipeline across all 30 features.
        Returns structured dictionary with features, feature_details, coverage, and warnings.
        """
        meta = validate_and_sanitize_url(url, enforce_public_dns=fetch_network)
        hostname = meta["hostname"]
        scheme = meta["scheme"]
        port = meta["port"]
        parsed = meta["parsed"]

        stages_status: Dict[str, Any] = {}
        features: Dict[str, Optional[int]] = {}
        feature_details: Dict[str, Dict[str, Any]] = {}
        warnings: List[str] = []

        # Stage 1: URL String (Lexical)
        try:
            lexical_feats = self.extract_lexical_features(url, parsed)
            features.update(lexical_feats)
            for k, v in lexical_feats.items():
                feature_details[k] = {
                    "name": k,
                    "value": v,
                    "status": FeatureStatus.OBSERVED,
                    "evidence_source": "url_lexical",
                    "explanation": f"Extracted directly from URL string lexical structure (value={v})",
                }
            stages_status["url_lexical"] = {
                "status": "success",
                "count": len(lexical_feats),
                "details": f"Extracted {len(lexical_feats)} lexical features from URL structure.",
            }
        except Exception as e:
            stages_status["url_lexical"] = {"status": "failed", "error": str(e), "count": 0}

        # Stage 2: DNS & TLS Inspection
        try:
            if mock_dns is not None:
                dns_feats = {
                    "DNSRecord": 1 if mock_dns else -1,
                    "SSLfinal_State": 1 if scheme == "https" and mock_dns else -1,
                }
                dns_status = FeatureStatus.OBSERVED
                dns_source = "network_dns"
            elif fetch_network:
                dns_feats = self.extract_dns_tls_features(hostname, scheme, port)
                dns_status = FeatureStatus.OBSERVED
                dns_source = "network_dns"
            else:
                dns_feats = {
                    "DNSRecord": 1,
                    "SSLfinal_State": 1 if scheme == "https" else -1,
                }
                dns_status = FeatureStatus.ESTIMATED
                dns_source = "heuristic_baseline"

            features.update(dns_feats)
            feature_details["DNSRecord"] = {
                "name": "DNSRecord",
                "value": dns_feats["DNSRecord"],
                "status": dns_status,
                "evidence_source": dns_source,
                "explanation": "DNS resolved host address" if dns_feats["DNSRecord"] == 1 else "DNS resolution failed",
            }
            feature_details["SSLfinal_State"] = {
                "name": "SSLfinal_State",
                "value": dns_feats["SSLfinal_State"],
                "status": dns_status,
                "evidence_source": "tls_handshake" if dns_status == FeatureStatus.OBSERVED else dns_source,
                "explanation": f"TLS certificate validation state ({dns_feats['SSLfinal_State']})",
            }

            stages_status["dns_tls"] = {
                "status": "success",
                "count": len(dns_feats),
                "details": f"DNS resolution: {'resolved' if dns_feats['DNSRecord']==1 else 'failed'}; TLS state: {dns_feats['SSLfinal_State']}.",
            }
        except Exception as e:
            stages_status["dns_tls"] = {"status": "failed", "error": str(e), "count": 0}

        # Stage 3: Safe HTML Content Inspection
        try:
            html_text = mock_html
            redirect_count = 0
            fetch_err = None

            if mock_html is None and fetch_network:
                html_text, redirect_count, fetch_err = self.safe_fetch_page(url, hostname)

            html_feats, html_details = self.extract_html_features(
                html_text, hostname, redirect_count, allow_heuristics=allow_heuristics
            )
            features.update(html_feats)
            feature_details.update(html_details)

            if fetch_err:
                warnings.append(f"Webpage fetch notice: {fetch_err}")
                stages_status["html_content"] = {
                    "status": "partial",
                    "count": len(html_feats),
                    "details": f"HTML fetch incomplete ({fetch_err}); neutral baselines applied.",
                }
            else:
                stages_status["html_content"] = {
                    "status": "success",
                    "count": len(html_feats),
                    "details": f"Parsed {len(html_feats)} DOM and behavioral attributes safely.",
                }
        except Exception as e:
            stages_status["html_content"] = {"status": "failed", "error": str(e), "count": 0}

        # Stage 4: External / Third-Party Intelligence
        is_live = features.get("DNSRecord", 1) == 1
        if allow_heuristics:
            heuristic_feats = self.get_documented_heuristic_features(is_accessible=is_live)
            features.update(heuristic_feats)
            for k, v in heuristic_feats.items():
                feature_details[k] = {
                    "name": k,
                    "value": v,
                    "status": FeatureStatus.ESTIMATED,
                    "evidence_source": "heuristic_baseline",
                    "explanation": f"Third-party service unavailable; neutral baseline {v} applied",
                }
            stages_status["external_intel"] = {
                "status": "heuristic_baseline",
                "count": len(heuristic_feats),
                "details": "Documented neutral baseline values applied for retired/commercial services.",
            }
            warnings.append(
                "External intelligence features (Alexa Rank, Google PageRank) use documented neutral baselines "
                "because original upstream APIs have been retired."
            )
        else:
            for k in STAGE_EXTERNAL_INTEL:
                features[k] = None
                feature_details[k] = {
                    "name": k,
                    "value": None,
                    "status": FeatureStatus.MISSING,
                    "evidence_source": "none",
                    "explanation": "Upstream third-party API is retired or unavailable in strict mode",
                }
            stages_status["external_intel"] = {
                "status": "unsupported",
                "count": 0,
                "reason": "Upstream third-party APIs (Alexa Rank, Google PageRank) are retired or require commercial feeds.",
            }

        # Compute metric coverage counts
        observed_count = sum(
            1 for d in feature_details.values()
            if d.get("status") in (FeatureStatus.OBSERVED, FeatureStatus.EXTERNALLY_VERIFIED)
        )
        estimated_count = sum(
            1 for d in feature_details.values()
            if d.get("status") == FeatureStatus.ESTIMATED
        )
        missing_count = sum(
            1 for d in feature_details.values()
            if d.get("status") == FeatureStatus.MISSING
        )

        unsupported_list = [
            k for k, d in feature_details.items()
            if d.get("status") == FeatureStatus.MISSING
        ]

        if missing_count > 0:
            coverage = "incomplete"
        elif estimated_count > 0:
            coverage = "heuristic"
        else:
            coverage = "complete"

        # Complete feature vector ordering
        complete_vector = {col: features.get(col) for col in EXPECTED_FEATURES}

        return {
            "url": url,
            "feature_coverage": coverage,
            "observed_count": observed_count,
            "estimated_count": estimated_count,
            "missing_count": missing_count,
            "extracted_count": len([v for v in features.values() if v is not None]),
            "total_expected": len(EXPECTED_FEATURES),
            "features": complete_vector,
            "feature_details": feature_details,
            "stages": stages_status,
            "unsupported_features": unsupported_list,
            "warnings": warnings,
        }
