from __future__ import annotations

import asyncio
import inspect
import json
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any

from ..database import db
from .events import Event, EventBus


def _now() -> float: return time.time()
def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float: return max(low, min(high, float(value)))

@dataclass
class WorkspaceCandidate:
    id: str; source: str; content: str; salience: float; confidence: float; urgency: float; novelty: float; relevance: float; created_at: float; ttl: float = 30.0; selected: bool = False; score: float = 0.0; cycle_id: str = ""
    def is_expired(self, now: float | None = None) -> bool:
        now = _now() if now is None else now; return self.ttl >= 0 and now > self.created_at + self.ttl

class GlobalWorkspaceV2:
    """Computational global-workspace coordination; not evidence of consciousness."""
    WEIGHTS = {"salience": .25, "confidence": .15, "urgency": .20, "novelty": .15, "relevance": .25}
    def __init__(self, events: EventBus | None = None):
        self.events=events; self.current=None; self.cycle_id=uuid.uuid4().hex[:12]; self.interrupted=False; self.subscribers=set(); self._ensure_schema()
    def _ensure_schema(self):
        db.execute("CREATE TABLE IF NOT EXISTS workspace_candidates_v2 (id TEXT PRIMARY KEY, source TEXT NOT NULL, content TEXT NOT NULL, salience REAL NOT NULL, confidence REAL NOT NULL, urgency REAL NOT NULL, novelty REAL NOT NULL, relevance REAL NOT NULL, created_at REAL NOT NULL, ttl REAL NOT NULL, selected INTEGER NOT NULL DEFAULT 0, score REAL NOT NULL DEFAULT 0, cycle_id TEXT NOT NULL)")
        db.execute("CREATE TABLE IF NOT EXISTS workspace_broadcasts_v2 (id INTEGER PRIMARY KEY AUTOINCREMENT, candidate_id TEXT NOT NULL, cycle_id TEXT NOT NULL, payload TEXT NOT NULL, interrupted INTEGER NOT NULL DEFAULT 0, created_at REAL NOT NULL)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_workspace_candidates_v2_created ON workspace_candidates_v2(created_at)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_workspace_broadcasts_v2_created ON workspace_broadcasts_v2(created_at)")
    def _score(self, values): return _clamp(sum(self.WEIGHTS[k]*_clamp(values.get(k,0)) for k in self.WEIGHTS))
    def submit_candidate(self, source, content, *, salience=.5, confidence=.5, urgency=.5, novelty=.5, relevance=.5, ttl=30.0):
        if not source.strip() or not content.strip(): raise ValueError("source and content are required")
        c=WorkspaceCandidate(uuid.uuid4().hex[:16],source.strip(),content.strip(),_clamp(salience),_clamp(confidence),_clamp(urgency),_clamp(novelty),_clamp(relevance),_now(),max(0,float(ttl)),False,0,self.cycle_id); c.score=self._score(asdict(c))
        db.execute("INSERT INTO workspace_candidates_v2 (id,source,content,salience,confidence,urgency,novelty,relevance,created_at,ttl,selected,score,cycle_id) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",(c.id,c.source,c.content,c.salience,c.confidence,c.urgency,c.novelty,c.relevance,c.created_at,c.ttl,0,c.score,c.cycle_id)); self._emit("workspace.candidate_added",{"candidate":asdict(c)}); return asdict(c)
    def clear_expired(self): return db.execute("DELETE FROM workspace_candidates_v2 WHERE created_at + ttl < ?",(_now(),)).rowcount
    def rank_candidates(self, limit=20):
        self.clear_expired(); return [dict(r) for r in db.fetchall("SELECT * FROM workspace_candidates_v2 WHERE cycle_id=? ORDER BY score DESC, created_at DESC LIMIT ?",(self.cycle_id,max(1,min(100,int(limit)))))]
    def select_winner(self):
        ranked=self.rank_candidates()
        if not ranked: self.current=None; return None
        w=ranked[0]; db.execute("UPDATE workspace_candidates_v2 SET selected=0 WHERE cycle_id=?",(self.cycle_id,)); db.execute("UPDATE workspace_candidates_v2 SET selected=1 WHERE id=?",(w["id"],)); self.current=WorkspaceCandidate(**{**w,"selected":True}); self._emit("workspace.selected",{"candidate":w,"cycle_id":self.cycle_id}); return dict(w)
    def broadcast(self,candidate_id=None,approved=True):
        if not approved: raise PermissionError("workspace broadcast requires approval")
        if candidate_id:
            row=db.fetchone("SELECT * FROM workspace_candidates_v2 WHERE id=?",(candidate_id,));
            if not row: raise KeyError(candidate_id)
            self.current=WorkspaceCandidate(**{**row,"selected":bool(row["selected"])})
        elif self.current is None: self.select_winner()
        if self.current is None: raise ValueError("no workspace candidate available")
        payload=asdict(self.current); db.execute("INSERT INTO workspace_broadcasts_v2 (candidate_id,cycle_id,payload,interrupted,created_at) VALUES (?,?,?,?,?)",(self.current.id,self.cycle_id,json.dumps(payload),int(self.interrupted),_now())); event={"candidate":payload,"subscribers":sorted(self.subscribers),"cycle_id":self.cycle_id,"interrupted":self.interrupted}; self._emit("workspace.broadcast",event); self.interrupted=False; return event
    def interrupt(self,reason="higher-priority candidate"):
        self.interrupted=True; winner=self.rank_candidates()[0] if self.rank_candidates() else None; self._emit("workspace.interruption",{"reason":reason,"candidate":winner,"cycle_id":self.cycle_id}); return {"interrupted":True,"reason":reason,"candidate":winner,"cycle_id":self.cycle_id}
    def subscribe(self,module_name):
        if not module_name.strip(): raise ValueError("module_name is required")
        self.subscribers.add(module_name.strip()); self._emit("workspace.subscribed",{"module":module_name.strip()}); return {"module":module_name.strip(),"subscribed":True}
    def unsubscribe(self,module_name): self.subscribers.discard(module_name.strip()); return {"module":module_name.strip(),"subscribed":False}
    def history(self,limit=50): return db.fetchall("SELECT * FROM workspace_broadcasts_v2 ORDER BY created_at DESC LIMIT ?",(max(1,min(200,int(limit))),))
    def snapshot(self): return {"cycle_id":self.cycle_id,"current":asdict(self.current) if self.current else None,"candidates":self.rank_candidates(),"subscribers":sorted(self.subscribers),"interrupted":self.interrupted,"history":self.history(20),"weights":self.WEIGHTS,"scientific_note":"Global Workspace V2 is a computational coordination mechanism, not evidence of subjective consciousness."}
    def _emit(self,event_type,payload):
        if not self.events: return
        try:
            result=self.events.publish(Event(type=event_type,payload=payload))
            if inspect.isawaitable(result):
                try: asyncio.get_running_loop().create_task(result)
                except RuntimeError: pass
        except Exception: pass
