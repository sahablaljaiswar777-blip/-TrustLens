"""Plain-language next-step recommendations for risk bands."""

from typing import Any, Dict
from engine.risk_engine import risk_band

_DECISIONS = {
    "TRUST": ("TRUST", "No strong warning signs were found by these offline checks.", "Proceed only if the request matches what you expected."),
    "LOW": ("VERIFY", "A small number of warning signs were found.", "Check the sender or destination through a contact method you already trust."),
    "CAUTION": ("CAUTION", "Several warning signs deserve attention.", "Pause before sharing information or paying; confirm using an independent channel."),
    "SUSPICIOUS": ("STOP", "Multiple warning signs combine into an elevated heuristic score.", "Do not follow the request yet. Contact the organization using a known-good number or website."),
    "HIGH RISK": ("STOP", "Strong warning signs were found in this submission.", "Do not share codes, credentials, or money. Verify independently before taking action."),
    "CRITICAL": ("CRITICAL", "The combined heuristic score is at the highest level.", "Stop and seek trusted, independent verification. Do not use contact details in the message."),
}


def decide(score: int) -> Dict[str, Any]:
    """Return decision label, risk band and human-readable guidance."""
    band = risk_band(score)
    label, explanation, recommendation = _DECISIONS[band]
    return {
        "band": band,
        "label": label,
        "explanation": explanation,
        "recommendation": recommendation,
    }
