from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from ..database import db

@dataclass
class InternalState:
    arousal: float = 0.20
    valence: float = 0.00
    uncertainty: float = 0.50
    energy: float = 1.00
    attention_load: float = 0.00
    stress: float = 0.00
    confidence: float = 0.50
    stability: float = 1.00

class InternalStateEngine:
    """Deterministic, inspectable internal-state simulation; not subjective experience."""
    def __init__(self):
        self.state = self._load()

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _load(self) -> InternalState:
        row = db.fetchone("SELECT value FROM settings WHERE key=?", ("internal_state",))
        if not row:
            return InternalState()
        try:
            import json
            return InternalState(**json.loads(row["value"]))
        except (ValueError, TypeError, KeyError):
            return InternalState()

    def _save(self) -> None:
        import json
        db.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            ("internal_state", json.dumps(asdict(self.state))),
        )

    def observe(self, *, input_length: int = 0, memory_count: int = 0, uncertainty: float | None = None) -> dict:
        load = self._clamp(input_length / 2000 + memory_count / 40)
        self.state.attention_load = load
        if uncertainty is not None:
            self.state.uncertainty = self._clamp(uncertainty)
        self.state.stress = self._clamp(0.55 * self.state.uncertainty + 0.45 * load)
        self.state.arousal = self._clamp(0.15 + 0.65 * load + 0.20 * self.state.stress)
        self.state.confidence = self._clamp(1.0 - self.state.uncertainty)
        self.state.energy = self._clamp(self.state.energy - 0.03 * load)
        self.state.stability = self._clamp(1.0 - 0.55 * self.state.stress - 0.25 * load)
        self._save()
        return asdict(self.state)

    def transition(self, *, uncertainty: float | None = None, energy_delta: float = 0.0, valence_delta: float = 0.0) -> dict:
        if uncertainty is not None:
            self.state.uncertainty = self._clamp(uncertainty)
        self.state.energy = self._clamp(self.state.energy + energy_delta)
        self.state.valence = self._clamp((self.state.valence + 1) / 2 + valence_delta) * 2 - 1
        self.state.confidence = self._clamp(1 - self.state.uncertainty)
        self.state.stress = self._clamp(0.55 * self.state.uncertainty + 0.45 * self.state.attention_load)
        self.state.stability = self._clamp(1 - 0.55 * self.state.stress - 0.25 * self.state.attention_load)
        self._save()
        return asdict(self.state)

    def recover(self, amount: float = 0.10) -> dict:
        self.state.energy = self._clamp(self.state.energy + amount)
        self.state.stress = self._clamp(self.state.stress - amount)
        self.state.arousal = self._clamp(self.state.arousal - amount * .5)
        self.state.attention_load = self._clamp(self.state.attention_load - amount)
        self.state.stability = self._clamp(1 - 0.55 * self.state.stress - 0.25 * self.state.attention_load)
        self._save()
        return asdict(self.state)

    def snapshot(self) -> dict:
        return asdict(self.state)

    def status(self) -> str:
        if self.state.stability < .35: return "unstable"
        if self.state.stress > .70: return "high_stress"
        if self.state.energy < .20: return "low_energy"
        if self.state.attention_load > .75: return "overloaded"
        return "stable"
