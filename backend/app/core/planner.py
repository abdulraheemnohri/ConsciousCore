from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from ..database import db
PLAN_STATUSES={"pending","running","completed","failed","skipped"}
@dataclass
class PlanStep:
    id:int; action:str; status:str="pending"; rationale:str=""; depends_on:list[int]|None=None
class Planner:
    def _row(self,row):
        return {"id":row["id"],"goal":row["goal"],"constraints":json.loads(row["constraints"] or "[]"),"steps":json.loads(row["steps"] or "[]"),"created_at":row["created_at"]}
    def create(self,goal,constraints=None):
        constraints=constraints or []; steps=[PlanStep(1,f"Clarify desired outcome for: {goal}",rationale="define success criteria",depends_on=[]),PlanStep(2,"Gather relevant memory and current workspace context",rationale="ground the plan",depends_on=[1]),PlanStep(3,f"Execute the smallest safe action toward: {goal}",rationale="make measurable progress",depends_on=[2]),PlanStep(4,"Observe result and evaluate against the goal",rationale="close action-observation loop",depends_on=[3]),PlanStep(5,"Reflect and update memory with the outcome",rationale="retain useful learning",depends_on=[4])]
        now=datetime.now(timezone.utc).isoformat(); cur=db.execute("INSERT INTO plans(goal,constraints,steps,created_at) VALUES(?,?,?,?)",(goal,json.dumps(constraints),json.dumps([asdict(x) for x in steps]),now)); return self._row(db.fetchone("SELECT * FROM plans WHERE id=?",(cur.lastrowid,)))
    def get(self,plan_id):
        row=db.fetchone("SELECT * FROM plans WHERE id=?",(plan_id,)); return self._row(row) if row else None
    def list(self,limit=100): return [self._row(r) for r in db.fetchall("SELECT * FROM plans ORDER BY id DESC LIMIT ?",(max(1,min(limit,1000)),))]
    def update_step(self,plan_id,step_id,status):
        if status not in PLAN_STATUSES: raise ValueError(f"invalid_plan_step_status:{status}")
        plan=self.get(plan_id)
        if not plan:return None
        for step in plan["steps"]:
            if step["id"]==step_id:
                deps=step.get("depends_on",[])
                if status in {"running","completed"} and any(next((x for x in plan["steps"] if x["id"]==d),{"status":"pending"})["status"]!="completed" for d in deps): raise ValueError("plan_step_dependencies_not_completed")
                step["status"]=status; break
        else:return None
        db.execute("UPDATE plans SET steps=? WHERE id=?",(json.dumps(plan["steps"]),plan_id)); return self.get(plan_id)
    def delete(self,plan_id): return db.execute("DELETE FROM plans WHERE id=?",(plan_id,)).rowcount>0
