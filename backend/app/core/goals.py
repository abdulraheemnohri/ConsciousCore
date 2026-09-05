from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from ..database import db

@dataclass
class Goal:
    id: int
    title: str
    priority: float = .5
    status: str = "active"
    progress: float = 0.0
    created_at: str = ""

class GoalManager:
    def add(self, title: str, priority: float = .5):
        now = datetime.now(timezone.utc).isoformat()
        cur = db.execute("INSERT INTO goals(title,priority,status,progress,created_at) VALUES(?,?,?,?,?)", (title, priority, "active", 0.0, now))
        return Goal(**db.fetchone("SELECT * FROM goals WHERE id=?", (cur.lastrowid,)))

    def update(self, goal_id: int, progress: float | None = None, status: str | None = None):
        goal = db.fetchone("SELECT * FROM goals WHERE id=?", (goal_id,))
        if not goal:
            return None
        new_progress = max(0, min(1, progress)) if progress is not None else goal["progress"]
        new_status = status or goal["status"]
        if new_progress >= 1:
            new_status = "completed"
        db.execute("UPDATE goals SET progress=?, status=? WHERE id=?", (new_progress, new_status, goal_id))
        return Goal(**db.fetchone("SELECT * FROM goals WHERE id=?", (goal_id,)))

    def snapshot(self):
        return [dict(row) for row in db.fetchall("SELECT * FROM goals ORDER BY id")]

    def active(self):
        return [dict(row) for row in db.fetchall("SELECT * FROM goals WHERE status='active' ORDER BY priority DESC, id")]
