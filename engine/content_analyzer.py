"""Heuristic checks for suspicious language in user-provided text."""

import re
from typing import Any, Dict, List

Signal = Dict[str, Any]

_PATTERNS = (
    ("urgent_action", re.compile(r"\b(urgent|immediately|act now|within \d+ hours?)\b", re.I), "Urgency pressure", 8),
    ("credential_request", re.compile(r"\b(password|passcode|login credentials|one[- ]time code|otp)\b", re.I), "Credential or code request", 18),
    ("payment_request", re.compile(r"\b(wire transfer|gift cards?|crypto(?:currency)?|payment required|pay now)\b", re.I), "Unusual payment request", 18),
    ("account_threat", re.compile(r"\b(account (?:will be|has been) (?:closed|suspended|locked)|legal action|arrest warrant)\b", re.I), "Threat or consequence", 14),
    ("link_prompt", re.compile(r"\b(click|tap|open|follow) (?:the |this )?(?:link|button|attachment)\b", re.I), "Prompt to open content", 6),
    ("sensitive_data", re.compile(r"\b(social security|bank details|card number|security answer)\b", re.I), "Sensitive information request", 16),
    ("prize_bait", re.compile(r"\b(you(?:'|’)ve|you have) won\b|\bclaim your (?:prize|reward)\b", re.I), "Unexpected prize claim", 12),
)


def analyze_content(text: str) -> List[Signal]:
    """Return one explainable signal for each language pattern found."""
    signals: List[Signal] = []
    for name, pattern, reason, points in _PATTERNS:
        if pattern.search(text):
            signals.append({
                "name": name,
                "category": "content",
                "severity": "high" if points >= 14 else "medium",
                "reason": reason + " language was detected.",
                "points": points,
            })
    return signals
