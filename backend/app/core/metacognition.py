from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass
class MetacognitiveState:
    confidence: float = .5
    uncertainty: float = .5
    evidence_strength: float = 0.0
    needs_verification: bool = True
    strategy: str = "retrieve → reason → verify"

class Metacognition:
    def evaluate(self, uncertainty: float, evidence_count: int) -> dict:
        evidence = min(1.0, evidence_count / 5)
        confidence = max(0.05, min(0.95, .7 * evidence + .3 * (1 - uncertainty)))
        state = MetacognitiveState(confidence, uncertainty, evidence, confidence < .65, "retrieve → reason → verify")
        return asdict(state)
