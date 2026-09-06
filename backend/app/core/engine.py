from dataclasses import dataclass, asdict
from .events import Event, EventBus
from .cognitive_event_bus_v2 import CognitiveEventBusV2
from .memory import MemoryStore
from .attention import AttentionEngine
from .goals import GoalManager
from .planner import Planner
from .reflection import ReflectionEngine
from .metacognition import Metacognition
from .prediction import PredictionEngine
from .world_model_v2 import WorldModelV2
from .global_workspace_v2 import GlobalWorkspaceV2
from .learning_v2 import LearningEngineV2
from .autobiographical_memory_v2 import AutobiographicalMemoryV2
from .settings_v2 import SettingsV2
from .safety import SafetyEngine
from .tools import ToolRegistry
from .sleep import SleepConsolidator
from .execution import ExecutionEngine
from .cognitive_loop import CognitiveLoop
from .internal_state import InternalStateEngine
from .self_model_v2 import SelfModelEngine
from ..models.fallback import FallbackModel
from ..models.manager import ModelManager
from ..runtime.orchestrator import RuntimeOrchestrator
from ..runtime.memory_federation import MemoryFederation

@dataclass
class SelfModel:
    identity: str = "ConsciousCore"; role: str = "local cognitive system"; architecture: str = "consciousness-inspired cognitive loop"; scientifically_conscious: bool = False

class CognitiveEngine:
    def __init__(self, model=None):
        self.model_manager = ModelManager(); self.model_manager.discover_gguf()
        self.model = model or self.model_manager.get_active() or FallbackModel()
        self.memory = MemoryStore(); self.events = CognitiveEventBusV2(); self.attention = AttentionEngine(); self.goals = GoalManager(); self.planner = Planner(); self.reflection = ReflectionEngine()
        self.metacognition = Metacognition(); self.prediction = PredictionEngine(); self.world = WorldModelV2(); self.safety = SafetyEngine(1); self.tools = ToolRegistry(self.safety); self.sleep = SleepConsolidator(self.memory)
        self.execution = ExecutionEngine(self.planner, self.safety, self.memory); self.internal_state = InternalStateEngine(); self.self_model_v2 = SelfModelEngine(); self.learning_v2 = LearningEngineV2(); self.autobiographical_v2 = AutobiographicalMemoryV2(); self.settings_v2 = SettingsV2()
        self.safety.autonomy_level = self.settings_v2.snapshot()["autonomy_level"]
        self.global_workspace_v2 = GlobalWorkspaceV2(self.events)
        self.runtime = RuntimeOrchestrator(self.model)
        self.memory_federation = MemoryFederation()
        self.state = self.internal_state.state; self.self_model = SelfModel(); self.workspace = {}; self.last_reflection = None; self.last_prediction = None; self.meta = {}; self.loop = CognitiveLoop(self)
        self._register_runtime_extensions()

    def _register_runtime_extensions(self):
        try:
            import inspect
            app = inspect.currentframe().f_back.f_globals.get("app")
            if app is not None and hasattr(app, "include_router"):
                from .autobiographical_api import create_router as auto_router
                from .settings_api import create_router as settings_router
                for prefix, factory in [("/api/autobiographical/v2",auto_router),("/api/settings/v2",settings_router)]:
                    if not any(getattr(r,"path","").startswith(prefix) for r in app.routes): app.include_router(factory(self))
        except Exception:
            pass

    def activate_model(self, model_id: str):
        info = self.model_manager.activate(model_id); self.model = self.model_manager.get_active(); self.runtime = RuntimeOrchestrator(self.model); return info

    async def process(self, message): return await self.loop.run(message)

    def snapshot(self):
        self_v2 = self.self_model_v2.assess(model_backend=self.model.info().get("backend", "unknown"), memory_count=self.memory.count(), active_goals=len(self.goals.active()))
        return {"state": self.internal_state.snapshot(), "self": asdict(self.self_model), "self_model_v2": self_v2, "workspace": self.workspace, "global_workspace_v2": self.global_workspace_v2.snapshot(), "memory_count": self.memory.count(), "goals": self.goals.snapshot(), "active_goals": self.goals.active(), "model": self.model.info(), "models": self.model_manager.list(), "runtime": self.runtime.snapshot(), "memory_federation": self.memory_federation.snapshot(), "reflection": asdict(self.last_reflection) if self.last_reflection else None, "metacognition": self.meta, "prediction": self.last_prediction, "world_model": self.world.snapshot(), "safety": self.safety.snapshot(), "tools": self.tools.snapshot(), "sleep": self.sleep.snapshot(), "execution": self.execution.snapshot(), "cognitive_loop": self.loop.snapshot(), "internal_state_status": self.internal_state.status(), "cognitive_events_v2": self.events.snapshot(), "learning_v2": self.learning_v2.snapshot(), "autobiographical_memory_v2": self.autobiographical_v2.snapshot(), "settings_v2": self.settings_v2.snapshot()}
