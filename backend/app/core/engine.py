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
from .execution import ExecutionEngine
from .cognitive_loop import CognitiveLoop
from .internal_state import InternalStateEngine
from .self_model_v2 import SelfModelEngine
from ..models.fallback import FallbackModel
from ..models.manager import ModelManager

@dataclass
class SelfModel:
    identity: str = "ConsciousCore"; role: str = "local cognitive system"; architecture: str = "consciousness-inspired cognitive loop"; scientifically_conscious: bool = False

class CognitiveEngine:
    def __init__(self, model=None):
        self.model_manager = ModelManager(); self.model_manager.discover_gguf()
        self.model = model or self.model_manager.get_active() or FallbackModel()
        self.memory = MemoryStore(); self.events = EventBus(); self.attention = AttentionEngine(); self.goals = GoalManager(); self.planner = Planner(); self.reflection = ReflectionEngine()
        self.metacognition = Metacognition(); self.prediction = PredictionEngine(); self.world = WorldModel(); self.safety = SafetyEngine(1); self.tools = ToolRegistry(self.safety); self.sleep = SleepConsolidator(self.memory)
        self.execution = ExecutionEngine(self.planner, self.safety, self.memory); self.internal_state = InternalStateEngine(); self.self_model_v2 = SelfModelEngine()
        self.state = self.internal_state.state; self.self_model = SelfModel(); self.workspace = {}; self.last_reflection = None; self.last_prediction = None; self.meta = {}; self.loop = CognitiveLoop(self)

    def activate_model(self, model_id: str):
        info = self.model_manager.activate(model_id); self.model = self.model_manager.get_active(); return info

    async def process(self, message): return await self.loop.run(message)

    def snapshot(self):
        self_v2 = self.self_model_v2.assess(model_backend=self.model.info().get("backend", "unknown"), memory_count=self.memory.count(), active_goals=len(self.goals.active()))
        return {"state": self.internal_state.snapshot(), "self": asdict(self.self_model), "self_model_v2": self_v2, "workspace": self.workspace, "memory_count": self.memory.count(), "goals": self.goals.snapshot(), "active_goals": self.goals.active(), "model": self.model.info(), "models": self.model_manager.list(), "reflection": asdict(self.last_reflection) if self.last_reflection else None, "metacognition": self.meta, "prediction": self.last_prediction, "world_model": self.world.snapshot(), "safety": self.safety.snapshot(), "tools": self.tools.snapshot(), "sleep": self.sleep.snapshot(), "execution": self.execution.snapshot(), "cognitive_loop": self.loop.snapshot(), "internal_state_status": self.internal_state.status()}
