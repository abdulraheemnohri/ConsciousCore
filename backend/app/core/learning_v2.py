from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any

from ..database import db


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


@dataclass
class LearningUpdate:
    id: str
    lesson: str
    strategy: str
    evidence: list[str]
    confidence: float
    impact: float
    source: str
    created_at: float
    applied: bool = False


class LearningEngineV2:
    """Bounded adaptation through lessons and strategy preferences; never rewrites model weights or source code."""

    def __init__(self):
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        db.execute("CREATE TABLE IF NOT EXISTS learning_updates_v2 (id TEXT PRIMARY KEY,lesson TEXT NOT NULL,strategy TEXT NOT NULL,evidence TEXT NOT NULL,confidence REAL NOT NULL,impact REAL NOT NULL,source TEXT NOT NULL,created_at REAL NOT NULL,applied INTEGER NOT NULL DEFAULT 0)")
        db.execute("CREATE TABLE IF NOT EXISTS learning_strategies_v2 (strategy TEXT PRIMARY KEY,score REAL NOT NULL DEFAULT 0.5,sample_count INTEGER NOT NULL DEFAULT 0,updated_at REAL NOT NULL)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_learning_updates_v2_created ON learning_updates_v2(created_at)")

    def learn(self, lesson: str, strategy: str, evidence: list[str] | None = None, confidence: float = .5, impact: float = .5, source: str = "reflection") -> dict[str, Any]:
        if not lesson.strip() or not strategy.strip():
            raise ValueError("lesson and strategy are required")
        item = LearningUpdate(uuid.uuid4().hex, lesson.strip(), strategy.strip(), evidence or [], _clamp(confidence), _clamp(impact), source.strip() or "reflection", time.time())
        db.execute("INSERT INTO learning_updates_v2 VALUES(?,?,?,?,?,?,?,?,?)", (item.id,item.lesson,item.strategy,json.dumps(item.evidence),item.confidence,item.impact,item.source,item.created_at,0))
        self._update_strategy(item.strategy, item.confidence * item.impact)
        return asdict(item)

    def _update_strategy(self, strategy: str, signal: float) -> None:
        row = db.fetchone("SELECT score,sample_count FROM learning_strategies_v2 WHERE strategy=?", (strategy,))
        now = time.time()
        if row:
            score = _clamp(float(row["score"]) * .8 + signal * .2)
            count = int(row["sample_count"]) + 1
            db.execute("UPDATE learning_strategies_v2 SET score=?,sample_count=?,updated_at=? WHERE strategy=?", (score,count,now,strategy))
        else:
            db.execute("INSERT INTO learning_strategies_v2(strategy,score,sample_count,updated_at) VALUES(?,?,?,?)", (strategy,_clamp(.5 + (signal-.5)*.5),1,now))

    def apply(self, update_id: str) -> dict[str, Any] | None:
        row = db.fetchone("SELECT * FROM learning_updates_v2 WHERE id=?", (update_id,))
        if not row:
            return None
        db.execute("UPDATE learning_updates_v2 SET applied=1 WHERE id=?", (update_id,))
        return self._decode(db.fetchone("SELECT * FROM learning_updates_v2 WHERE id=?", (update_id,)))

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = db.fetchall("SELECT * FROM learning_updates_v2 ORDER BY created_at DESC LIMIT ?", (max(1,min(500,int(limit))),))
        return [self._decode(r) for r in rows]

    def strategies(self, limit: int = 50) -> list[dict[str, Any]]:
        return [dict(r) for r in db.fetchall("SELECT * FROM learning_strategies_v2 ORDER BY score DESC, sample_count DESC LIMIT ?", (max(1,min(200,int(limit))),))]

    def recommend(self, candidates: list[str]) -> dict[str, Any]:
        if not candidates:
            return {"strategy": None, "reason": "no candidates"}
        placeholders = ",".join("?" for _ in candidates)
        rows = db.fetchall(f"SELECT strategy,score,sample_count FROM learning_strategies_v2 WHERE strategy IN ({placeholders}) ORDER BY score DESC,sample_count DESC", tuple(candidates))
        if rows:
            return {"strategy": rows[0]["strategy"], "score": rows[0]["score"], "sample_count": rows[0]["sample_count"], "reason": "highest learned strategy score"}
        return {"strategy": candidates[0], "score": .5, "sample_count": 0, "reason": "no prior evidence; neutral default"}

    def stats(self) -> dict[str, Any]:
        u = db.fetchone("SELECT COUNT(*) AS n FROM learning_updates_v2")["n"]
        a = db.fetchone("SELECT COUNT(*) AS n FROM learning_updates_v2 WHERE applied=1")["n"]
        s = db.fetchone("SELECT COUNT(*) AS n FROM learning_strategies_v2")["n"]
        return {"updates": u, "applied": a, "strategies": s}

    @staticmethod
    def _decode(row) -> dict[str, Any]:
        item = dict(row)
        try: item["evidence"] = json.loads(item["evidence"])
        except Exception: pass
        item["applied"] = bool(item.get("applied"))
        return item

    def snapshot(self) -> dict[str, Any]:
        return {"recent": self.recent(20), "strategies": self.strategies(20), "stats": self.stats(), "bounded": True, "scientific_note": "Learning V2 adapts memories and strategy preferences; it does not establish consciousness, rewrite model weights, or modify arbitrary source code."}
