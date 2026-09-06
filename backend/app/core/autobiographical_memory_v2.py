from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import re
from ..database import db

_MAX = 12000

def _clip(value: str | None, limit: int = _MAX) -> str:
    value = str(value or "")
    return value if len(value) <= limit else value[:limit] + "…"

def _safe_tags(tags):
    if not tags:
        return []
    return [str(x)[:80] for x in list(tags)[:32]]

@dataclass
class Episode:
    id: int
    cycle_id: int | None
    started_at: str
    ended_at: str
    title: str
    summary: str
    input_text: str
    response_summary: str
    active_goal_id: int | None
    plan_id: int | None
    reflection_id: int | None
    learning_ids: list[int]
    event_ids: list[int]
    importance: float
    confidence: float
    tags: list[str]
    metadata: dict
    archived: bool
    created_at: str

class AutobiographicalMemoryV2:
    """Persistent computational history of important cognitive cycles.

    This is an autobiographical-style timeline, not subjective experience,
    consciousness, sentience, or proof that the system experiences events.
    """
    def __init__(self):
        db.execute("""CREATE TABLE IF NOT EXISTS autobiographical_episodes_v2(
            id INTEGER PRIMARY KEY AUTOINCREMENT, cycle_id INTEGER, started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL,
            input_text TEXT NOT NULL, response_summary TEXT NOT NULL, active_goal_id INTEGER,
            plan_id INTEGER, reflection_id INTEGER, learning_ids TEXT NOT NULL,
            event_ids TEXT NOT NULL, importance REAL NOT NULL, confidence REAL NOT NULL,
            tags TEXT NOT NULL, metadata TEXT NOT NULL, archived INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL)""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_auto_v2_cycle ON autobiographical_episodes_v2(cycle_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_auto_v2_time ON autobiographical_episodes_v2(started_at DESC)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_auto_v2_archived ON autobiographical_episodes_v2(archived)")

    @staticmethod
    def _clamp(value, default=.5):
        try: return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError): return default

    def _row(self, row) -> dict:
        d = dict(row)
        d["learning_ids"] = json.loads(d.pop("learning_ids") or "[]")
        d["event_ids"] = json.loads(d.pop("event_ids") or "[]")
        d["tags"] = json.loads(d.pop("tags") or "[]")
        d["metadata"] = json.loads(d.pop("metadata") or "{}")
        d["archived"] = bool(d["archived"])
        return d

    def create(self, cycle_id=None, title="Cognitive episode", summary="", input_text="", response_summary="",
               active_goal_id=None, plan_id=None, reflection_id=None, learning_ids=None, event_ids=None,
               importance=.5, confidence=.5, tags=None, metadata=None, started_at=None, ended_at=None):
        now = datetime.now(timezone.utc).isoformat()
        started_at = started_at or now; ended_at = ended_at or now
        title = _clip(title, 240).strip() or "Cognitive episode"
        summary = _clip(summary, 4000); input_text = _clip(input_text); response_summary = _clip(response_summary, 4000)
        tags = _safe_tags(tags); metadata = metadata if isinstance(metadata, dict) else {}
        db.execute("""INSERT INTO autobiographical_episodes_v2
            (cycle_id,started_at,ended_at,title,summary,input_text,response_summary,active_goal_id,plan_id,reflection_id,learning_ids,event_ids,importance,confidence,tags,metadata,archived,created_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (cycle_id,started_at,ended_at,title,summary,input_text,response_summary,active_goal_id,plan_id,reflection_id,
             json.dumps(list(learning_ids or [])[:100]),json.dumps(list(event_ids or [])[:100]),self._clamp(importance),self._clamp(confidence),json.dumps(tags),json.dumps(metadata)[:20000],0,now))
        row = db.fetchone("SELECT * FROM autobiographical_episodes_v2 WHERE id=last_insert_rowid()")
        return self._row(row)

    def get(self, episode_id: int):
        row = db.fetchone("SELECT * FROM autobiographical_episodes_v2 WHERE id=?", (episode_id,))
        return self._row(row) if row else None

    def list(self, limit=50, include_archived=False):
        sql = "SELECT * FROM autobiographical_episodes_v2"
        if not include_archived: sql += " WHERE archived=0"
        sql += " ORDER BY started_at DESC, id DESC LIMIT ?"
        return [self._row(r) for r in db.fetchall(sql, (max(1, min(int(limit), 500)),))]

    def search(self, query: str, limit=50, include_archived=False):
        q = _clip(query, 500).strip().lower()
        if not q: return self.list(limit, include_archived)
        rows = self.list(500, include_archived)
        terms = [x for x in re.split(r"\s+", q) if x]
        scored=[]
        for e in rows:
            hay = " ".join([e["title"], e["summary"], e["input_text"], e["response_summary"], " ".join(e["tags"]) ]).lower()
            score = sum(2 if t in e["title"].lower() else 1 for t in terms if t in hay)
            if score: scored.append((score, e))
        scored.sort(key=lambda x: (x[0], x[1]["started_at"]), reverse=True)
        return [e for _, e in scored[:max(1, min(int(limit), 500))]]

    def timeline(self, start=None, end=None, limit=100):
        clauses=[]; args=[]
        if start: clauses.append("started_at>=?"); args.append(start)
        if end: clauses.append("started_at<=?"); args.append(end)
        sql="SELECT * FROM autobiographical_episodes_v2 WHERE archived=0"
        if clauses: sql += " AND " + " AND ".join(clauses)
        sql += " ORDER BY started_at ASC, id ASC LIMIT ?"; args.append(max(1,min(int(limit),1000)))
        return [self._row(r) for r in db.fetchall(sql, tuple(args))]

    def archive(self, episode_id: int, archived=True):
        db.execute("UPDATE autobiographical_episodes_v2 SET archived=? WHERE id=?", (1 if archived else 0, episode_id))
        return self.get(episode_id)

    def stats(self):
        total = db.fetchone("SELECT COUNT(*) AS n FROM autobiographical_episodes_v2")["n"]
        active = db.fetchone("SELECT COUNT(*) AS n FROM autobiographical_episodes_v2 WHERE archived=0")["n"]
        avg = db.fetchone("SELECT COALESCE(AVG(importance),0) AS v FROM autobiographical_episodes_v2 WHERE archived=0")["v"]
        return {"total": total, "active": active, "archived": total-active, "average_importance": round(float(avg),4)}

    def snapshot(self):
        return {"stats": self.stats(), "recent": self.list(20), "scientific_boundary": "Computational autobiographical history; not subjective experience."}
