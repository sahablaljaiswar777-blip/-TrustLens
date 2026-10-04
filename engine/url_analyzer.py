"""Offline URL string checks. This module never opens or fetches a URL."""

import ipaddress
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

Signal = Dict[str, Any]
_SHORTENERS = {"bit.ly", "t.co", "tinyurl.com", "goo.gl", "is.gd", "ow.ly"}
_TRUSTED_WORDS = {"paypal", "microsoft", "apple", "google", "amazon", "bank"}
_NON_WEB_SCHEMES = {"data", "file", "javascript", "mailto", "tel", "vbscript"}


def _host_from_url(value: str) -> Optional[str]:
    candidate = value.strip()
    if not candidate:
        return None
    if "://" not in candidate:
        candidate = "https://" + candidate
    try:
        return (urlsplit(candidate).hostname or "").lower().rstrip(".") or None
    except ValueError:
        return None


def analyze_url(value: str) -> List[Signal]:
    """Inspect URL syntax and hostname only; no DNS or network operations occur."""
    candidate = value.strip()
    if not candidate:
        return []
    signals: List[Signal] = []

    def add(name: str, category: str, reason: str, points: int, severity: str) -> None:
        signals.append({
            "name": name, "category": category, "severity": severity,
            "reason": reason, "points": points,
        })

    scheme_match = re.match(r"^([a-z][a-z0-9+.-]*):", candidate, re.I)
    if scheme_match and (
        "://" in candidate or scheme_match.group(1).lower() in _NON_WEB_SCHEMES
    ) and scheme_match.group(1).lower() not in {"http", "https"}:
        add("unusual_scheme", "url", "The URL uses a scheme other than HTTP or HTTPS.", 18, "high")
        return signals

    if len(candidate) > 120:
        add("long_url", "url", "The URL is unusually long and may hide its destination.", 7, "low")
    if re.search(r"%(?:2f|5c|40|2e)", candidate, re.I):
        add("encoded_delimiters", "url", "Encoded delimiters can make a destination harder to read.", 8, "medium")
    if "@" in candidate.split("://")[-1].split("/")[0]:
        add("userinfo_url", "url", "Text before @ can disguise the actual URL host.", 20, "high")

    host = _host_from_url(candidate)
    if host is None:
        add("invalid_url", "url", "The URL could not be parsed as a recognizable address.", 10, "medium")
        return signals

    try:
        ipaddress.ip_address(host.strip("[]"))
        add("ip_host", "url", "The URL uses a raw IP address instead of a recognizable domain.", 14, "high")
    except ValueError:
        pass
    if host.startswith("xn--") or ".xn--" in host:
        add("punycode_host", "url", "The hostname contains punycode, which can obscure look-alike characters.", 16, "high")
    if host in _SHORTENERS or any(host.endswith("." + item) for item in _SHORTENERS):
        add("shortened_url", "url", "A link-shortening domain hides the final destination.", 18, "medium")
    labels = host.split(".")
    for trusted in _TRUSTED_WORDS:
        if any(trusted in label and label != trusted for label in labels):
            add("brand_like_host", "url", "A hostname contains a brand-like word without being that exact domain.", 18, "high")
            break
    if len(labels) >= 5:
        add("many_subdomains", "url", "The hostname has many subdomains, which can obscure its registered domain.", 7, "low")

    try:
        parsed = urlsplit(candidate if "://" in candidate else "https://" + candidate)
        if parsed.scheme.lower() not in {"http", "https"}:
            add("unusual_scheme", "url", "The URL uses a scheme other than HTTP or HTTPS.", 18, "high")
        elif parsed.scheme.lower() == "http":
            add("unencrypted_http", "url", "The link uses HTTP rather than encrypted HTTPS.", 8, "medium")
    except ValueError:
        pass
    return signals
