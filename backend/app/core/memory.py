from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import re
from ..database import db, decode_memory

MEMORY_KINDS = {"working", "episodic", "semantic", "procedural", "self", "meta"}

@dataclass
class Memory:
    id: int
    kind: str
    content: str
    importance: float = .5
    confidence: float = .7
    created_at: str = ""
    metadata: dict | None = None
    tags: list[str] | None = None
    source: str = "system"
    access_count: int = 0
    last_accessed: str | None = None
    consolidated: bool = False

    def json(self):
        return asdict(self)

class MemoryStore:
    def add(self, content, kind="episodic", importance=.5, confidence=.7, metadata=None, tags=None, source="system"):
        kind = kind if kind in MEMORY_KINDS else "episodic"
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute(
            "INSERT INTO memories(kind,content,importance,confidence,tags,source,metadata,created_at) VALUES(?,?,?,?,?,?,?,?)",
            (kind, content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now),
        )
        row = db.fetchone("SELECT * FROM memories WHERE id=?", (cur.lastrowid,))
        return Memory(**decode_memory(row))

    def _row_to_memory(self, row):
        return Memory(**decode_memory(row))

    def search(self, q, limit=8):
        terms = set(re.findall(r"\w+", q.lower()))
        rows = db.fetchall("SELECT * FROM memories ORDER BY created_at DESC LIMIT 5000")
        scored = []
        now = datetime.now(timezone.utc)
        for row in rows:
            words = set(re.findall(r"\w+", row["content"].lower()))
            overlap = len(terms & words) / (len(terms) or 1)
            score = .65 * overlap + .20 * row["importance"] + .15 * row["confidence"]
            if score:
                scored.append((score, self._row_to_memory(row)))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [m for _, m in scored[:limit]]
        for m in results:
            db.execute("UPDATE memories SET access_count=access_count+1,last_accessed=? WHERE id=?", (now.isoformat(), m.id))
        return results

    def recent(self, limit=20):
        rows = db.fetchall("SELECT * FROM memories ORDER BY id DESC LIMIT ?", (limit,))
        return [self._row_to_memory(r) for r in reversed(rows)]

    def count(self):
        row = db.fetchone("SELECT COUNT(*) AS n FROM memories")
        return int(row["n"])

    def consolidate(self):
        cur = db.execute("UPDATE memories SET consolidated=1 WHERE importance >= 0.65 OR access_count >= 2")
        return cur.rowcount

    def all(self):
        return self.recent(1000)
