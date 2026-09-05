from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from ..database import db

@dataclass
class Entity:
    id: str
    label: str
    kind: str = "concept"
    created_at: str = ""

@dataclass
class Relation:
    source: str
    relation: str
    target: str
    confidence: float = .5
    created_at: str = ""

class WorldModel:
    def add_entity(self, entity_id: str, label: str, kind: str = "concept"):
        now = datetime.now(timezone.utc).isoformat()
        db.execute("INSERT INTO world_entities(id,label,kind,created_at) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET label=excluded.label, kind=excluded.kind", (entity_id, label, kind, now))
        row = db.fetchone("SELECT * FROM world_entities WHERE id=?", (entity_id,))
        return row

    def relate(self, source: str, relation: str, target: str, confidence: float = .5):
        now = datetime.now(timezone.utc).isoformat()
        confidence = max(0, min(1, confidence))
        cur = db.execute("INSERT INTO world_relations(source,relation,target,confidence,created_at) VALUES(?,?,?,?,?)", (source, relation, target, confidence, now))
        return db.fetchone("SELECT * FROM world_relations WHERE id=?", (cur.lastrowid,))

    def snapshot(self):
        return {"entities": db.fetchall("SELECT id,label,kind,created_at FROM world_entities ORDER BY id"), "relations": db.fetchall("SELECT source,relation,target,confidence,created_at FROM world_relations ORDER BY id")}
