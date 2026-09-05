from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
from ..database import db

@dataclass
class Reflection:
    summary: str
    lessons: list[str]
    uncertainties: list[str]
    next_actions: list[str]
    created_at: str

class ReflectionEngine:
    def reflect(self, input_text: str, response: str, memory_count: int, uncertainty: float) -> Reflection:
        lessons = ["Use retrieved context when it is relevant.", "Do not treat internal state as proof of subjective consciousness."]
        uncertainties = ["Confidence remains limited when retrieved evidence is sparse."] if uncertainty > .5 else []
        actions = ["Verify important assumptions before external action."]
        reflection = Reflection(
            summary=f"Reviewed one cognitive cycle with {memory_count} stored memories.",
            lessons=lessons,
            uncertainties=uncertainties,
            next_actions=actions,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        db.execute("INSERT INTO reflections(summary,lessons,uncertainties,next_actions,created_at) VALUES(?,?,?,?,?)", (reflection.summary, json.dumps(reflection.lessons), json.dumps(reflection.uncertainties), json.dumps(reflection.next_actions), reflection.created_at))
        return reflection

    def recent(self, limit: int = 20):
        rows = db.fetchall("SELECT * FROM reflections ORDER BY id DESC LIMIT ?", (max(1, min(limit, 1000)),))
        return [{**r, "lessons": json.loads(r["lessons"]), "uncertainties": json.loads(r["uncertainties"]), "next_actions": json.loads(r["next_actions"])} for r in rows]
