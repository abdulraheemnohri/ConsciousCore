from dataclasses import dataclass, asdict
from .events import Event, EventBus
from .memory import MemoryStore
from .attention import AttentionEngine
from .goals import GoalManager
from .planner import Planner
from .reflection import ReflectionEngine
from .metacognition import Metacognition
from .prediction import PredictionEngine
from .world_model import WorldModel
from .safety import SafetyEngine
from .tools import ToolRegistry
from .sleep import SleepConsolidator
from ..models.fallback import FallbackModel
from ..models.manager import ModelManager

@dataclass
class InternalState:
    arousal: float = .2; valence: float = 0; uncertainty: float = .5; energy: float = 1

@dataclass
class SelfModel:
    identity: str = "ConsciousCore"; role: str = "local cognitive system"; architecture: str = "consciousness-inspired cognitive loop"; scientifically_conscious: bool = False

class CognitiveEngine:
    def __init__(self, model=None):
        self.model_manager = ModelManager()
        self.model_manager.discover_gguf()
        self.model = model or self.model_manager.get_active() or FallbackModel()
        self.memory = MemoryStore(); self.events = EventBus()
        self.attention = AttentionEngine(); self.goals = GoalManager(); self.planner = Planner(); self.reflection = ReflectionEngine()
        self.metacognition = Metacognition(); self.prediction = PredictionEngine(); self.world = WorldModel()
        self.safety = SafetyEngine(1); self.tools = ToolRegistry(self.safety); self.sleep = SleepConsolidator(self.memory)
        self.state = InternalState(); self.self_model = SelfModel(); self.workspace = {}; self.last_reflection = None; self.last_prediction = None; self.meta = {}

    def activate_model(self, model_id: str):
        info = self.model_manager.activate(model_id)
        self.model = self.model_manager.get_active()
        return info

    async def process(self, message):
        memories = self.memory.search(message); ranked = self.attention.score(message, [m.content for m in memories], urgency=self.state.arousal)
        self.state.uncertainty = max(.05, .8 - len(memories) * .1); self.meta = self.metacognition.evaluate(self.state.uncertainty, len(memories)); self.last_prediction = self.prediction.predict(message, self.state.uncertainty)
        self.workspace = {"input": message, "focus": message, "attention": [asdict(x) for x in ranked], "memories": [m.json() for m in memories], "model": self.model.info(), "metacognition": self.meta, "prediction": self.last_prediction}
        await self.events.publish(Event("workspace.updated", self.workspace)); response = await self.model.generate(message, [m.content for m in memories])
        saved = self.memory.add("User: " + message + "\nSystem: " + response, kind="episodic", importance=.55, confidence=max(.1, 1-self.state.uncertainty), source="conversation")
        self.last_reflection = self.reflection.reflect(message, response, self.memory.count(), self.state.uncertainty)
        await self.events.publish(Event("memory.created", saved.json())); await self.events.publish(Event("reflection.created", asdict(self.last_reflection)))
        return {"response": response, "memories": [m.json() for m in memories], "state": asdict(self.state), "workspace": self.workspace, "reflection": asdict(self.last_reflection), "metacognition": self.meta, "prediction": self.last_prediction}

    def snapshot(self):
        return {"state": asdict(self.state), "self": asdict(self.self_model), "workspace": self.workspace, "memory_count": self.memory.count(), "goals": self.goals.snapshot(), "active_goals": self.goals.active(), "model": self.model.info(), "models": self.model_manager.list(), "reflection": asdict(self.last_reflection) if self.last_reflection else None, "metacognition": self.meta, "prediction": self.last_prediction, "world_model": self.world.snapshot(), "safety": self.safety.snapshot(), "tools": self.tools.snapshot(), "sleep": self.sleep.snapshot()}
