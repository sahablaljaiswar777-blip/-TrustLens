"""Deterministic aggregation of explainable signal points."""

from typing import Any, Dict, Iterable, Set

BANDS = (
    (19, "TRUST"),
    (39, "LOW"),
    (59, "CAUTION"),
    (79, "SUSPICIOUS"),
    (94, "HIGH RISK"),
    (100, "CRITICAL"),
)


def calculate_score(signals: Iterable[Dict[str, Any]]) -> int:
    """Sum bounded signal points and small deterministic correlation bonuses."""
    signal_list = list(signals)
    points = sum(max(0, min(25, int(signal.get("points", 0)))) for signal in signal_list)
    categories: Set[str] = {str(signal.get("category", "")) for signal in signal_list}
    names_by_category: Dict[str, Set[str]] = {}
    for signal in signal_list:
        category = str(signal.get("category", ""))
        names_by_category.setdefault(category, set()).add(str(signal.get("name", "")))
    repeated_category_count = sum(
        1 for names in names_by_category.values() if len(names) >= 2
    )
    if len(categories) >= 2:
        points += 5
    if len(categories) >= 4:
        points += 5
    points += min(10, repeated_category_count * 5)
    return max(0, min(100, points))


def risk_band(score: int) -> str:
    """Map an integer score into one of the published score ranges."""
    bounded = max(0, min(100, int(score)))
    for upper_bound, band in BANDS:
        if bounded <= upper_bound:
            return band
    return "CRITICAL"
