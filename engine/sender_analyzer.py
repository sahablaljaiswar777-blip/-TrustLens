"""Heuristic sender and claimed-organization consistency checks."""

import re
from typing import Any, Dict, List

Signal = Dict[str, Any]


def analyze_sender(sender: str, claimed_organization: str) -> List[Signal]:
    """Compare submitted sender text with a claimed organization; verify neither."""
    sender = sender.strip()
    organization = claimed_organization.strip()
    signals: List[Signal] = []
    if not sender or not organization:
        return signals

    domains = re.findall(r"[\w.-]+\.[A-Za-z]{2,}", sender.lower())
    org_key = re.sub(r"[^a-z0-9]", "", organization.lower())
    if domains:
        domain_key = re.sub(r"[^a-z0-9]", "", domains[-1].split(".")[0])
        if org_key and org_key not in domain_key and domain_key not in org_key:
            signals.append({
                "name": "sender_org_mismatch",
                "category": "sender",
                "severity": "medium",
                "reason": "The sender address text does not obviously match the claimed organization.",
                "points": 14,
            })
    else:
        signals.append({
            "name": "sender_unstructured",
            "category": "sender",
            "severity": "low",
            "reason": "The supplied sender text does not contain a recognizable email-like domain.",
            "points": 4,
        })
    return signals
