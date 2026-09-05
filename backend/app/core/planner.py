from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

from ..database import db

PLAN_STATUSES = {"pending", "running", "completed", "failed", "skipped"}

@dataclass
class PlanStep:
    id: int
    action: str
    status: str = "pending"
    rationale: str = ""

class Planner:
    def _row(self, row) -> dict:
        return {
            "id": row["id"],
            "goal": row["goal"],
            "constraints": json.loads(row["constraints"] or "[]"),
            "steps": json.loads(row["steps"] or "[]"),
            "created_at": row["created_at"],
        }

    def create(self, goal: str, constraints: list[str] | None = None) -> dict:
        constraints = constraints or []
        steps = [
            PlanStep(1, f"Clarify desired outcome for: {goal}", rationale="define success criteria"),
            PlanStep(2, "Gather relevant memory and current workspace context", rationale="ground the plan in available context"),
            PlanStep(3, f"Execute the smallest safe action toward: {goal}", rationale="progress while minimizing risk"),
            PlanStep(4, "Observe result and evaluate against the goal", rationale="close the action-observation loop"),
            PlanStep(5, "Reflect and update memory with the outcome", rationale="retain useful learning"),
        ]
        now = datetime.now(timezone.utc).isoformat()
        cursor = db.execute(
            "INSERT INTO plans(goal,constraints,steps,created_at) VALUES(?,?,?,?)",
            (goal, json.dumps(constraints), json.dumps([asdict(x) for x in steps]), now),
        )
        row = db.fetchone("SELECT * FROM plans WHERE id=?", (cursor.lastrowid,))
        return self._row(row)

    def get(self, plan_id: int) -> dict | None:
        row = db.fetchone("SELECT * FROM plans WHERE id=?", (plan_id,))
        return self._row(row) if row else None

    def list(self, limit: int = 100) -> list[dict]:
        rows = db.fetchall("SELECT * FROM plans ORDER BY id DESC LIMIT ?", (max(1, min(limit, 1000)),))
        return [self._row(row) for row in rows]

    def update_step(self, plan_id: int, step_id: int, status: str) -> dict | None:
        if status not in PLAN_STATUSES:
            raise ValueError(f"invalid_plan_step_status:{status}")
        plan = self.get(plan_id)
        if not plan:
            return None
        found = False
        for step in plan["steps"]:
            if step["id"] == step_id:
                step["status"] = status
                found = True
                break
        if not found:
            return None
        db.execute("UPDATE plans SET steps=? WHERE id=?", (json.dumps(plan["steps"]), plan_id))
        return self.get(plan_id)

    def delete(self, plan_id: int) -> bool:
        cursor = db.execute("DELETE FROM plans WHERE id=?", (plan_id,))
        return cursor.rowcount > 0
