from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from ..database import db

GOAL_STATUSES={"active","paused","completed","cancelled"}
@dataclass
class Goal:
    id:int; title:str; priority:float=.5; status:str="active"; progress:float=0.0; created_at:str=""
class GoalManager:
    def add(self,title:str,priority:float=.5):
        now=datetime.now(timezone.utc).isoformat(); cur=db.execute("INSERT INTO goals(title,priority,status,progress,created_at) VALUES(?,?,?,?,?)",(title,max(0,min(1,priority)),"active",0.0,now)); return Goal(**db.fetchone("SELECT * FROM goals WHERE id=?",(cur.lastrowid,)))
    def get(self,goal_id:int):
        row=db.fetchone("SELECT * FROM goals WHERE id=?",(goal_id,)); return Goal(**row) if row else None
    def update(self,goal_id:int,progress:float|None=None,status:str|None=None,priority:float|None=None):
        goal=self.get(goal_id)
        if not goal:return None
        if status is not None and status not in GOAL_STATUSES: raise ValueError(f"invalid_goal_status:{status}")
        p=max(0,min(1,progress)) if progress is not None else goal.progress; s=status or goal.status
        if p>=1:s="completed"
        pr=max(0,min(1,priority)) if priority is not None else goal.priority
        db.execute("UPDATE goals SET progress=?,status=?,priority=? WHERE id=?",(p,s,pr,goal_id)); return self.get(goal_id)
    def delete(self,goal_id:int)->bool:
        return db.execute("DELETE FROM goals WHERE id=?",(goal_id,)).rowcount>0
    def snapshot(self): return [dict(row) for row in db.fetchall("SELECT * FROM goals ORDER BY priority DESC,id")]
    def active(self): return [dict(row) for row in db.fetchall("SELECT * FROM goals WHERE status='active' ORDER BY priority DESC,id")]
