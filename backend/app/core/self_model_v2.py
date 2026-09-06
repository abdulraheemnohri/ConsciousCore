from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from ..database import db

@dataclass
class SelfModelV2:
    name: str = "ConsciousCore"
    role: str = "local cognitive runtime"
    architecture: str = "consciousness-inspired cognitive architecture"
    version: str = "2"
    scientifically_conscious: bool = False
    local_only: bool = True
    autonomy_level: int = 1
    capabilities: tuple[str, ...] = (
        "memory retrieval and persistence",
        "goal management",
        "planning and reflection",
        "metacognitive uncertainty tracking",
        "world-model representation",
        "local model inference when configured",
        "safe local state transitions",
    )
    limitations: tuple[str, ...] = (
        "does not establish subjective consciousness or sentience",
        "does not have human-like feelings or experiences",
        "does not execute arbitrary external actions silently",
        "does not bypass authentication, MFA, CAPTCHA, or extract secrets",
        "does not rewrite its own model weights autonomously",
        "local model quality depends on the configured hardware and model",
    )
    boundaries: tuple[str, ...] = (
        "external actions require the safety and approval layer",
        "runtime state is computational control state, not subjective experience",
        "learning changes memory, strategies, and configuration rather than unrestricted source code",
    )
    updated_at: str = ""

class SelfModelEngine:
    """Inspectable self-representation; it is not evidence of consciousness."""
    KEY = "self_model_v2"
    def __init__(self):
        self.model = self._load()

    def _load(self) -> SelfModelV2:
        row = db.fetchone("SELECT value FROM settings WHERE key=?", (self.KEY,))
        if not row:
            return SelfModelV2(updated_at=datetime.now(timezone.utc).isoformat())
        try:
            data = json.loads(row["value"])
            base = asdict(SelfModelV2())
            base.update(data)
            for key in ("capabilities", "limitations", "boundaries"):
                base[key] = tuple(base[key])
            return SelfModelV2(**base)
        except (ValueError, TypeError, KeyError):
            return SelfModelV2(updated_at=datetime.now(timezone.utc).isoformat())

    def _save(self):
        db.execute(
            "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (self.KEY, json.dumps(asdict(self.model))),
        )

    def snapshot(self) -> dict:
        return asdict(self.model)

    def assess(self, *, model_backend: str, memory_count: int, active_goals: int) -> dict:
        return {
            **self.snapshot(),
            "runtime": {
                "model_backend": model_backend,
                "memory_records": memory_count,
                "active_goals": active_goals,
                "ready": True,
            },
        }

    def update_role(self, role: str | None = None, autonomy_level: int | None = None) -> dict:
        if role is not None:
            role = role.strip()
            if role:
                self.model.role = role[:200]
        if autonomy_level is not None:
            self.model.autonomy_level = max(0, min(3, int(autonomy_level)))
        self.model.updated_at = datetime.now(timezone.utc).isoformat()
        self._save()
        return self.snapshot()
