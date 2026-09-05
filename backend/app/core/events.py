from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import asyncio

@dataclass
class Event:
    type: str
    payload: dict
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EventBus:
    def __init__(self): self._queues=set()
    def subscribe(self):
        q=asyncio.Queue(); self._queues.add(q); return q
    def unsubscribe(self,q): self._queues.discard(q)
    async def publish(self,event):
        for q in list(self._queues): await q.put(event)
