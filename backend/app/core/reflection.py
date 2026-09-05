from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

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
        return Reflection(
            summary=f"Reviewed one cognitive cycle with {memory_count} stored memories.",
            lessons=lessons,
            uncertainties=uncertainties,
            next_actions=actions,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
