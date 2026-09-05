from __future__ import annotations
from dataclasses import dataclass
import re

@dataclass
class AttentionItem:
    content: str
    score: float
    reason: str

class AttentionEngine:
    def score(self, query: str, candidates: list[str], urgency: float = .5) -> list[AttentionItem]:
        q = set(re.findall(r"\w+", query.lower()))
        results = []
        for content in candidates:
            words = set(re.findall(r"\w+", content.lower()))
            relevance = len(q & words) / (len(q) or 1)
            score = min(1.0, .75 * relevance + .25 * max(0, min(1, urgency)))
            if score > 0:
                results.append(AttentionItem(content, round(score, 4), "lexical relevance + urgency"))
        return sorted(results, key=lambda x: x.score, reverse=True)
