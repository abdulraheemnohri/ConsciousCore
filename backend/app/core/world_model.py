from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass
class Entity:
    id: str
    label: str
    kind: str = "concept"

@dataclass
class Relation:
    source: str
    relation: str
    target: str
    confidence: float = .5

class WorldModel:
    def __init__(self): self.entities: dict[str, Entity] = {}; self.relations: list[Relation] = []
    def add_entity(self, entity_id: str, label: str, kind: str = "concept"):
        self.entities[entity_id] = Entity(entity_id, label, kind); return asdict(self.entities[entity_id])
    def relate(self, source: str, relation: str, target: str, confidence: float = .5):
        r = Relation(source, relation, target, max(0, min(1, confidence))); self.relations.append(r); return asdict(r)
    def snapshot(self): return {"entities": [asdict(x) for x in self.entities.values()], "relations": [asdict(x) for x in self.relations]}
