"""Checks for common social-engineering persuasion patterns."""

import re
from typing import Any, Dict, List

Signal = Dict[str, Any]

_PATTERNS = (
    ("secrecy_request", re.compile(r"\b(don't tell|do not tell|keep this (?:secret|confidential))\b", re.I), "Secrecy or isolation request", 14),
    ("authority_pressure", re.compile(r"\b(ceo|director|police|tax authority|government agent)\b", re.I), "Authority framing", 6),
    ("bypass_process", re.compile(r"\b(skip (?:the )?usual process|bypass (?:the )?(?:usual )?(?:approval|process)|don't verify|do not verify)\b", re.I), "Request to bypass normal checks", 18),
    ("emotional_pressure", re.compile(r"\b(emergency|family member in trouble|final warning|last chance)\b", re.I), "Emotional or deadline pressure", 9),
)


def analyze_social_engineering(text: str) -> List[Signal]:
    """Return signals for persuasion tactics without claiming malicious intent."""
    return [
        {
            "name": name,
            "category": "social_engineering",
            "severity": "high" if points >= 14 else "medium",
            "reason": reason + " may be worth independently checking.",
            "points": points,
        }
        for name, pattern, reason, points in _PATTERNS
        if pattern.search(text)
    ]
