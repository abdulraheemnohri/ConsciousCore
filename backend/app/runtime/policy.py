from __future__ import annotations

from dataclasses import dataclass
import re


SECRET_PATTERNS = (
    re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|secret|private[_-]?key)\b\s*[:=]\s*\S+"),
    re.compile(r"\b\d{13,19}\b"),
)


@dataclass(slots=True)
class BoundaryDecision:
    classification: str
    cloud_allowed: bool
    remote_allowed: bool
    redacted_prompt: str
    reasons: list[str]


def classify(text: str, requested: str = "private") -> BoundaryDecision:
    hits = [pattern.search(text) for pattern in SECRET_PATTERNS]
    secret = any(hits)
    classification = "secret" if secret else requested.lower()
    if classification not in {"public", "internal", "private", "sensitive", "secret"}:
        classification = "private"
    cloud_allowed = classification in {"public", "internal"}
    remote_allowed = classification != "secret"
    redacted = text
    reasons: list[str] = []
    if secret:
        redacted = re.sub(r"(?i)(\b(?:api[_-]?key|access[_-]?token|secret|private[_-]?key)\b\s*[:=]\s*)\S+", r"\1[REDACTED]", redacted)
        reasons.append("secret-like material detected")
    if classification in {"sensitive", "secret"}:
        reasons.append("privacy policy prefers local processing")
    return BoundaryDecision(classification, cloud_allowed, remote_allowed, redacted, reasons)
