from __future__ import annotations
from datetime import datetime, timezone
from .memory import MemoryStore

class SleepConsolidator:
    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.last_run: str | None = None

    def run(self) -> dict:
        consolidated = self.memory.consolidate()
        self.last_run = datetime.now(timezone.utc).isoformat()
        return {"consolidated": consolidated, "timestamp": self.last_run, "mode": "local_memory_consolidation"}

    def snapshot(self):
        return {"last_run": self.last_run}
