from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from ..database import db


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass
class WorldEntity:
    id: str
    label: str
    kind: str = "concept"
    properties: dict = None
    confidence: float = 0.5
    active: bool = True
    created_at: str = ""
    updated_at: str = ""


@dataclass
class WorldRelationship:
    id: int | None
    source: str
    relation: str
    target: str
    confidence: float = 0.5
    valid_from: str = ""
    valid_to: str | None = None
    properties: dict = None
    created_at: str = ""


class WorldModelV2:
    """Persistent world representation with temporal state and epistemic uncertainty.

    This is a computational belief/knowledge store, not objective truth or evidence
    of consciousness. Predictions and contradiction detection are heuristic.
    """

    def _entity(self, row):
        if not row:
            return None
        return {**row, "properties": json.loads(row.get("properties") or "{}"), "active": bool(row.get("active", 1))}

    def add_entity(self, entity_id: str, label: str, kind: str = "concept", properties: dict | None = None, confidence: float = .5):
        ts = now(); confidence = clamp(confidence)
        existing = db.fetchone("SELECT id FROM world_entities_v2 WHERE id=?", (entity_id,))
        if existing:
            db.execute("UPDATE world_entities_v2 SET label=?,kind=?,properties=?,confidence=?,active=1,updated_at=? WHERE id=?", (label, kind, json.dumps(properties or {}), confidence, ts, entity_id))
            action = "updated"
        else:
            db.execute("INSERT INTO world_entities_v2(id,label,kind,properties,confidence,active,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?)", (entity_id, label, kind, json.dumps(properties or {}), confidence, 1, ts, ts))
            action = "created"
        db.execute("INSERT INTO world_entity_history_v2(entity_id,action,state,created_at) VALUES(?,?,?,?)", (entity_id, action, json.dumps(self._entity(db.fetchone("SELECT * FROM world_entities_v2 WHERE id=?", (entity_id,)))), ts))
        return self._entity(db.fetchone("SELECT * FROM world_entities_v2 WHERE id=?", (entity_id,)))

    def update_entity(self, entity_id: str, **changes):
        current = self._entity(db.fetchone("SELECT * FROM world_entities_v2 WHERE id=?", (entity_id,)))
        if not current:
            return None
        label = changes.get("label", current["label"]); kind = changes.get("kind", current["kind"])
        props = changes.get("properties", current["properties"]); confidence = clamp(changes.get("confidence", current["confidence"]))
        active = int(changes.get("active", current["active"])); ts = now()
        db.execute("UPDATE world_entities_v2 SET label=?,kind=?,properties=?,confidence=?,active=?,updated_at=? WHERE id=?", (label, kind, json.dumps(props), confidence, active, ts, entity_id))
        updated = self._entity(db.fetchone("SELECT * FROM world_entities_v2 WHERE id=?", (entity_id,)))
        db.execute("INSERT INTO world_entity_history_v2(entity_id,action,state,created_at) VALUES(?,?,?,?)", (entity_id, "updated", json.dumps(updated), ts))
        return updated

    def add_relation(self, source: str, relation: str, target: str, confidence: float = .5, valid_from: str | None = None, valid_to: str | None = None, properties: dict | None = None):
        ts = now(); vf = valid_from or ts; confidence = clamp(confidence)
        cur = db.execute("INSERT INTO world_relations_v2(source,relation,target,confidence,valid_from,valid_to,properties,created_at) VALUES(?,?,?,?,?,?,?,?)", (source, relation, target, confidence, vf, valid_to, json.dumps(properties or {}), ts))
        return db.fetchone("SELECT * FROM world_relations_v2 WHERE id=?", (cur.lastrowid,))

    def close_relation(self, relation_id: int, valid_to: str | None = None):
        ts = valid_to or now(); db.execute("UPDATE world_relations_v2 SET valid_to=? WHERE id=?", (ts, relation_id))
        return db.fetchone("SELECT * FROM world_relations_v2 WHERE id=?", (relation_id,))

    def add_event(self, event_type: str, entity_ids: list[str] | None = None, payload: dict | None = None, timestamp: str | None = None, source: str = "system"):
        ts = timestamp or now()
        cur = db.execute("INSERT INTO world_events_v2(event_type,entity_ids,payload,timestamp,source) VALUES(?,?,?,?,?)", (event_type, json.dumps(entity_ids or []), json.dumps(payload or {}), ts, source))
        return db.fetchone("SELECT * FROM world_events_v2 WHERE id=?", (cur.lastrowid,))

    def add_belief(self, statement: str, confidence: float = .5, evidence_refs: list[str] | None = None, status: str = "uncertain"):
        ts = now(); confidence = clamp(confidence)
        cur = db.execute("INSERT INTO world_beliefs_v2(statement,confidence,evidence_refs,status,created_at,updated_at) VALUES(?,?,?,?,?,?)", (statement, confidence, json.dumps(evidence_refs or []), status, ts, ts))
        return db.fetchone("SELECT * FROM world_beliefs_v2 WHERE id=?", (cur.lastrowid,))

    def detect_contradictions(self):
        rows = db.fetchall("SELECT id,source,relation,target,confidence,valid_from,valid_to,properties FROM world_relations_v2 ORDER BY id")
        contradictions = []
        # Explicit inverse pairs are treated as contradictions only when they overlap in time.
        inverse = {("is", "is_not"), ("has", "does_not_have"), ("supports", "contradicts")}
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                if a["source"] == b["source"] and a["target"] == b["target"] and (a["relation"], b["relation"]) in inverse | {(y, x) for x, y in inverse}:
                    if not a["valid_to"] or not b["valid_to"] or a["valid_to"] >= b["valid_from"] and b["valid_to"] >= a["valid_from"]:
                        contradictions.append({"type": "relation_conflict", "left": a, "right": b, "uncertainty": round(1 - min(a["confidence"], b["confidence"]), 4)})
        return contradictions

    def history(self, entity_id: str):
        return db.fetchall("SELECT entity_id,action,state,created_at FROM world_entity_history_v2 WHERE entity_id=? ORDER BY id", (entity_id,))

    def query(self, text: str):
        q = f"%{text}%"
        return {
            "entities": [self._entity(r) for r in db.fetchall("SELECT * FROM world_entities_v2 WHERE label LIKE ? OR kind LIKE ? ORDER BY confidence DESC", (q, q))],
            "relations": db.fetchall("SELECT * FROM world_relations_v2 WHERE relation LIKE ? OR source LIKE ? OR target LIKE ? ORDER BY confidence DESC", (q, q, q)),
            "beliefs": db.fetchall("SELECT * FROM world_beliefs_v2 WHERE statement LIKE ? ORDER BY confidence DESC", (q,)),
        }

    def snapshot(self):
        entities = [self._entity(r) for r in db.fetchall("SELECT * FROM world_entities_v2 ORDER BY id")]
        relations = db.fetchall("SELECT * FROM world_relations_v2 ORDER BY id")
        events = db.fetchall("SELECT * FROM world_events_v2 ORDER BY timestamp DESC LIMIT 100")
        beliefs = db.fetchall("SELECT * FROM world_beliefs_v2 ORDER BY updated_at DESC")
        contradictions = self.detect_contradictions()
        return {"entities": entities, "relations": relations, "events": events, "beliefs": beliefs, "contradictions": contradictions, "uncertainty": round(sum([e["confidence"] for e in entities]) / len(entities), 4) if entities else 0.0}
