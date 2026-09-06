from __future__ import annotations

import json
import time
import uuid
from typing import Any, Callable

from ..database import db
from .events import Event, EventBus


class CognitiveEventBusV2(EventBus):
    """Persistent unified cognitive timeline. It records computation events, not subjective experience."""

    def __init__(self, max_payload: int = 50000):
        super().__init__()
        self.max_payload = max_payload
        self._subscribers_v2: set[Callable[[dict[str, Any]], None]] = set()
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        db.execute("CREATE TABLE IF NOT EXISTS cognitive_events_v2 (id TEXT PRIMARY KEY,event_type TEXT NOT NULL,phase TEXT NOT NULL,source TEXT NOT NULL,cycle_id TEXT,payload TEXT NOT NULL,importance REAL NOT NULL DEFAULT 0.5,timestamp REAL NOT NULL,correlation_id TEXT,parent_event_id TEXT,visibility TEXT NOT NULL DEFAULT 'timeline')")
        db.execute("CREATE INDEX IF NOT EXISTS idx_cognitive_events_v2_time ON cognitive_events_v2(timestamp)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_cognitive_events_v2_cycle ON cognitive_events_v2(cycle_id,timestamp)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_cognitive_events_v2_phase ON cognitive_events_v2(phase,timestamp)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_cognitive_events_v2_type ON cognitive_events_v2(event_type,timestamp)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_cognitive_events_v2_source ON cognitive_events_v2(source,timestamp)")

    @staticmethod
    def _clamp(v: float) -> float:
        return max(0.0, min(1.0, float(v)))

    def record(self, event_type: str, *, phase: str = "system", source: str = "system", cycle_id: str | None = None, payload: dict[str, Any] | None = None, importance: float = .5, correlation_id: str | None = None, parent_event_id: str | None = None, visibility: str = "timeline") -> dict[str, Any]:
        if not event_type.strip():
            raise ValueError("event_type is required")
        payload = payload or {}
        encoded = json.dumps(payload, default=str)
        if len(encoded) > self.max_payload:
            encoded = json.dumps({"truncated": True, "preview": encoded[: self.max_payload - 80]})
        item = {"id": uuid.uuid4().hex, "event_type": event_type.strip(), "phase": phase.strip() or "system", "source": source.strip() or "system", "cycle_id": cycle_id, "payload": payload, "importance": self._clamp(importance), "timestamp": time.time(), "correlation_id": correlation_id, "parent_event_id": parent_event_id, "visibility": visibility.strip() or "timeline"}
        db.execute("INSERT INTO cognitive_events_v2 (id,event_type,phase,source,cycle_id,payload,importance,timestamp,correlation_id,parent_event_id,visibility) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (item["id"],item["event_type"],item["phase"],item["source"],item["cycle_id"],encoded,item["importance"],item["timestamp"],correlation_id,parent_event_id,item["visibility"]))
        for callback in list(self._subscribers_v2):
            try: callback(item)
            except Exception: pass
        return item

    async def publish(self, event: Event):
        payload = event.payload if isinstance(event.payload, dict) else {"value": event.payload}
        meta = payload.get("_cognitive", {}) if isinstance(payload.get("_cognitive"), dict) else {}
        self.record(event.type, phase=str(meta.get("phase", event.type.split(".")[0] if "." in event.type else "system")), source=str(meta.get("source", "event_bus")), cycle_id=meta.get("cycle_id"), payload=payload, importance=float(meta.get("importance", .5)), correlation_id=meta.get("correlation_id"), parent_event_id=meta.get("parent_event_id"))
        await super().publish(event)

    def query(self, *, cycle_id: str | None = None, phase: str | None = None, source: str | None = None, event_type: str | None = None, limit: int = 100, before: float | None = None, after: float | None = None) -> list[dict[str, Any]]:
        clauses, args = [], []
        for col, value in (("cycle_id",cycle_id),("phase",phase),("source",source),("event_type",event_type)):
            if value: clauses.append(f"{col}=?"); args.append(value)
        if before is not None: clauses.append("timestamp<?"); args.append(float(before))
        if after is not None: clauses.append("timestamp>?"); args.append(float(after))
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        rows = db.fetchall(f"SELECT * FROM cognitive_events_v2{where} ORDER BY timestamp DESC LIMIT ?", (*args, max(1,min(1000,int(limit)))))
        return [self._decode(r) for r in rows]

    def timeline(self, limit: int = 100, cycle_id: str | None = None) -> list[dict[str, Any]]:
        return list(reversed(self.query(cycle_id=cycle_id, limit=limit)))

    def by_cycle(self, cycle_id: str, limit: int = 500) -> list[dict[str, Any]]:
        return self.timeline(limit, cycle_id)

    def by_phase(self, phase: str, limit: int = 100) -> list[dict[str, Any]]:
        return list(reversed(self.query(phase=phase, limit=limit)))

    def latest(self, limit: int = 20) -> list[dict[str, Any]]:
        return self.query(limit=limit)

    def stats(self) -> dict[str, Any]:
        total = db.fetchone("SELECT COUNT(*) AS n FROM cognitive_events_v2")["n"]
        phases = db.fetchall("SELECT phase,COUNT(*) AS n FROM cognitive_events_v2 GROUP BY phase ORDER BY n DESC")
        types = db.fetchall("SELECT event_type,COUNT(*) AS n FROM cognitive_events_v2 GROUP BY event_type ORDER BY n DESC LIMIT 20")
        cycles = db.fetchone("SELECT COUNT(DISTINCT cycle_id) AS n FROM cognitive_events_v2 WHERE cycle_id IS NOT NULL")["n"]
        return {"total": total, "cycles": cycles, "phases": [dict(r) for r in phases], "event_types": [dict(r) for r in types]}

    def subscribe_v2(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers_v2.add(callback)

    def unsubscribe_v2(self, callback: Callable[[dict[str, Any]], None]) -> None:
        self._subscribers_v2.discard(callback)

    @staticmethod
    def _decode(row) -> dict[str, Any]:
        item = dict(row)
        try: item["payload"] = json.loads(item["payload"])
        except Exception: pass
        return item

    def snapshot(self) -> dict[str, Any]:
        return {"latest": self.latest(20), "stats": self.stats(), "scientific_note": "The timeline represents computational events and coordination, not subjective experience or proof of consciousness."}
