"""Orchestration for a complete offline TrustLens analysis."""

from typing import Any, Dict, List
from engine.content_analyzer import analyze_content
from engine.decision_engine import decide
from engine.risk_engine import calculate_score
from engine.sender_analyzer import analyze_sender
from engine.social_engineering import analyze_social_engineering
from engine.url_analyzer import analyze_url


def analyze_submission(
    message: str = "",
    url: str = "",
    email_context: str = "",
    qr_url: str = "",
    sender: str = "",
    claimed_organization: str = "",
) -> Dict[str, Any]:
    """Analyze submitted strings without making any network requests."""
    text = "\n".join(part for part in (message, email_context) if part)
    signals: List[Dict[str, Any]] = []
    signals.extend(analyze_content(text))
    signals.extend(analyze_social_engineering(text))
    signals.extend(analyze_url(url))
    signals.extend(analyze_url(qr_url))
    signals.extend(analyze_sender(sender, claimed_organization))
    score = calculate_score(signals)
    decision = decide(score)
    return {
        "score": score,
        "band": decision["band"],
        "decision": decision["label"],
        "explanation": decision["explanation"],
        "recommendation": decision["recommendation"],
        "signals": signals,
        "signal_count": len(signals),
        "categories": sorted({signal["category"] for signal in signals}),
        "heuristic_notice": "Heuristic indicators only. This result does not verify identity, intent, or whether a link is safe.",
    }
