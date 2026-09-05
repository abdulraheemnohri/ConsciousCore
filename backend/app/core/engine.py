from dataclasses import dataclass, asdict
from .events import Event, EventBus
from .memory import MemoryStore
from ..models.fallback import FallbackModel

@dataclass
class InternalState:
    arousal: float = .2
    valence: float = 0
    uncertainty: float = .5
    energy: float = 1

@dataclass
class SelfModel:
    identity: str = "ConsciousCore"
    role: str = "local cognitive system"
    architecture: str = "consciousness-inspired cognitive loop"
    scientifically_conscious: bool = False

class CognitiveEngine:
    def __init__(self, model=None):
        self.model = model or FallbackModel()
        self.memory = MemoryStore()
        self.events = EventBus()
        self.state = InternalState()
        self.self_model = SelfModel()
        self.workspace = {}
        self.goals = []

    async def process(self, message):
        memories = self.memory.search(message)
        self.workspace = {
            "input": message,
            "focus": message,
            "attention_score": 1.0,
            "memories": [m.json() for m in memories],
            "model": self.model.info(),
        }
        self.state.uncertainty = max(.05, .8 - len(memories) * .1)
        await self.events.publish(Event("workspace.updated", self.workspace))
        response = await self.model.generate(message, [m.content for m in memories])
        saved = self.memory.add(
            "User: " + message + "\nSystem: " + response,
            kind="episodic",
            importance=.55,
            confidence=max(.1, 1 - self.state.uncertainty),
            source="conversation",
        )
        await self.events.publish(Event("memory.created", saved.json()))
        return {
            "response": response,
            "memories": [m.json() for m in memories],
            "state": asdict(self.state),
            "workspace": self.workspace,
        }

    def snapshot(self):
        return {
            "state": asdict(self.state),
            "self": asdict(self.self_model),
            "workspace": self.workspace,
            "memory_count": self.memory.count(),
            "goals": self.goals,
            "model": self.model.info(),
        }
