from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class Prediction:
    statement: str
    probability: float
    basis: str
    created_at: str

class PredictionEngine:
    def predict(self, observation: str, uncertainty: float) -> dict:
        probability = max(.05, min(.95, 1 - uncertainty))
        return asdict(Prediction(
            statement=f"If the current context remains stable, the next useful step is to continue processing: {observation[:240]}",
            probability=round(probability, 3),
            basis="heuristic state-based prediction; not a guaranteed forecast",
            created_at=datetime.now(timezone.utc).isoformat(),
        ))
