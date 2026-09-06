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
    def json(self): return asdict(self)

class MemoryStore:
    def add(self, content, kind="episodic", importance=.5, confidence=.7, metadata=None, tags=None, source="system"):
        kind = kind if kind in MEMORY_KINDS else "episodic"
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute("INSERT INTO memories(kind,content,importance,confidence,tags,source,metadata,created_at) VALUES(?,?,?,?,?,?,?,?)", (kind, content, float(importance), float(confidence), json.dumps(tags or []), source, json.dumps(metadata or {}), now))
        return self.get(cur.lastrowid)

    def _row_to_memory(self, row): return Memory(**decode_memory(row))
    def get(self, memory_id):
        row = db.fetchone("SELECT * FROM memories WHERE id=?", (memory_id,))
        return self._row_to_memory(row) if row else None

    def search(self, q, limit=8, kind=None, consolidated=None):
        terms = set(re.findall(r"\w+", q.lower()))
        clauses, params = [], []
        if kind in MEMORY_KINDS: clauses.append("kind=?"); params.append(kind)
        if consolidated is not None: clauses.append("consolidated=?"); params.append(int(consolidated))
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        rows = db.fetchall(f"SELECT * FROM memories{where} ORDER BY created_at DESC LIMIT 5000", tuple(params))
        scored=[]; now=datetime.now(timezone.utc)
        for row in rows:
            words=set(re.findall(r"\w+", row["content"].lower())); overlap=len(terms & words)/(len(terms) or 1)
            tag_words=set(re.findall(r"\w+", " ".join(json.loads(row.get("tags") or "[]")).lower()))
            tag_overlap=len(terms & tag_words)/(len(terms) or 1)
            score=.60*overlap+.10*tag_overlap+.20*row["importance"]+.10*row["confidence"]
            if score or not q: scored.append((score,self._row_to_memory(row)))
        scored.sort(key=lambda x:x[0], reverse=True)
        results=[m for _,m in scored[:max(1,min(limit,1000))]]
        for m in results: db.execute("UPDATE memories SET access_count=access_count+1,last_accessed=? WHERE id=?", (now.isoformat(),m.id))
        return results

    def recent(self, limit=20, kind=None, consolidated=None):
        return self.search("", limit, kind, consolidated)
    def count(self): return int(db.fetchone("SELECT COUNT(*) AS n FROM memories")["n"])
    def stats(self):
        total=self.count(); by_kind={r["kind"]:r["n"] for r in db.fetchall("SELECT kind,COUNT(*) n FROM memories GROUP BY kind")}; consolidated=int(db.fetchone("SELECT COUNT(*) n FROM memories WHERE consolidated=1")["n"])
        return {"total":total,"consolidated":consolidated,"pending":total-consolidated,"by_kind":by_kind}
    def update(self, memory_id, importance=None, confidence=None, kind=None, tags=None, source=None, consolidated=None):
        current=self.get(memory_id)
        if not current: return None
        values=[]; params=[]
        for col,val in (("importance",importance),("confidence",confidence),("kind",kind),("tags",json.dumps(tags) if tags is not None else None),("source",source),("consolidated",int(consolidated) if consolidated is not None else None)):
            if val is not None: values.append(f"{col}=?"); params.append(val)
        if not values: return current
        params.append(memory_id); db.execute(f"UPDATE memories SET {', '.join(values)} WHERE id=?",tuple(params)); return self.get(memory_id)
    def delete(self, memory_id): return db.execute("DELETE FROM memories WHERE id=?",(memory_id,)).rowcount>0
    def consolidate(self): return db.execute("UPDATE memories SET consolidated=1 WHERE importance >= 0.65 OR access_count >= 2").rowcount
    def all(self): return self.recent(1000)
