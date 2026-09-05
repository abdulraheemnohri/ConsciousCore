from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import re

@dataclass
class Memory:
    id:int; kind:str; content:str; importance:float=.5; confidence:float=.7; created_at:str=''; metadata:dict|None=None
    def json(self): return asdict(self)

class MemoryStore:
    def __init__(self): self.items=[]; self.next_id=1
    def add(self,content,kind='episodic',importance=.5,confidence=.7,metadata=None):
        m=Memory(self.next_id,kind,content,importance,confidence,datetime.now(timezone.utc).isoformat(),metadata or {})
        self.next_id+=1; self.items.append(m); return m
    def search(self,q,limit=8):
        terms=set(re.findall(r'\\w+',q.lower())); scored=[]
        for m in self.items:
            words=set(re.findall(r'\\w+',m.content.lower())); overlap=len(terms&words)/(len(terms) or 1)
            score=.75*overlap+.25*m.importance
            if score: scored.append((score,m))
        scored.sort(key=lambda x:x[0],reverse=True); return [m for _,m in scored[:limit]]
