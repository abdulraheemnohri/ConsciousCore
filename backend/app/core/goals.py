from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class Goal:
    id: int
    title: str
    priority: float = .5
    status: str = "active"
    progress: float = 0.0
    created_at: str = ""

class GoalManager:
    def __init__(self): self.items: list[Goal] = []; self.next_id = 1
    def add(self, title: str, priority: float = .5):
        g = Goal(self.next_id, title, priority, "active", 0.0, datetime.now(timezone.utc).isoformat())
        self.next_id += 1; self.items.append(g); return g
    def update(self, goal_id: int, progress: float | None = None, status: str | None = None):
        g = next((x for x in self.items if x.id == goal_id), None)
        if not g: return None
        if progress is not None: g.progress = max(0, min(1, progress))
        if status is not None: g.status = status
        if g.progress >= 1: g.status = "completed"
        return g
    def active(self): return [asdict(g) for g in sorted(self.items, key=lambda x: x.priority, reverse=True) if x.status == "active"]
    def snapshot(self): return [asdict(g) for g in self.items]
