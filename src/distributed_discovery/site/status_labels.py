"""Human presentation labels for machine-oriented study and evidence statuses."""

from __future__ import annotations

PHASE_LABELS = {
    "foundations": "Foundations",
    "exact-result": "Exact in this model",
    "complete-bounded-study": "Completed finite study",
    "active-extension": "Active research",
    "registered": "Planned study",
    "registered-optional": "Planned study",
    "queued": "Planned study",
    "blocked": "Paused",
    "retired": "Retired",
}

REGISTRY_LABELS = {
    "complete-bounded-study": "Completed finite study",
    "active-extension": "Active research",
    "registered": "Planned study",
    "registered-optional": "Planned study",
    "queued": "Planned study",
    "blocked": "Paused",
}


def human_status(value: object, *, kind: str = "phase") -> str:
    """Return a concise label while leaving the raw value available to callers."""
    raw = str(value or "").strip()
    normalized = raw.lower()
    if kind == "phase":
        return PHASE_LABELS.get(normalized, _fallback(raw))
    if kind == "registry":
        return REGISTRY_LABELS.get(normalized, PHASE_LABELS.get(normalized, _fallback(raw)))
    if kind == "publication":
        if normalized == "validated-repository-paper":
            return "Validated working paper"
        return _fallback(raw)
    if "no-result" in normalized or "registration-only" in normalized:
        return "Open question"
    if "synthetic" in normalized:
        return "Synthetic only"
    if "independently-reproduced" in normalized or "independent" in normalized:
        return "Checked independently"
    if "exact" in normalized or "verified" in normalized:
        return "Checked evidence"
    return _fallback(raw)


def _fallback(value: str) -> str:
    words = " ".join(part for part in value.replace("_", "-").split("-") if part)
    return words.capitalize() if words else "Status unavailable"
