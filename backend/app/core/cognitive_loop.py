from __future__ import annotations
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from .events import Event
from ..runtime.types import RuntimeMode, RuntimeRequest

PHASES = [
    "input", "perception", "attention", "workspace", "memory", "self_world",
    "internal_state", "goal_evaluation", "reasoning", "planning", "safety",
    "execution", "observation", "reflection", "learning", "consolidation", "idle"
]

@dataclass
class CognitiveCycle:
    cycle_id: int = 0
    phase: str = "idle"
    status: str = "idle"
    input_text: str = ""
    active_goal: dict | None = None
    plan_id: int | None = None
    completed_phases: list[str] = field(default_factory=list)
    started_at: str | None = None
    updated_at: str | None = None
    error: str | None = None

class CognitiveLoop:
    """Observable coordinator for a bounded consciousness-inspired cognitive loop."""
    def __init__(self, engine):
        self.engine = engine
        self.counter = 0
        self.current = CognitiveCycle()

    async def _phase(self, name: str, payload: dict | None = None):
        self.current.phase = name
        self.current.updated_at = datetime.now(timezone.utc).isoformat()
        if name not in self.current.completed_phases:
            self.current.completed_phases.append(name)
        await self.engine.events.publish(Event(f"loop.{name}", payload or {"cycle_id": self.current.cycle_id}))

    async def run(self, message: str):
        self.counter += 1
        now = datetime.now(timezone.utc).isoformat()
        self.current = CognitiveCycle(self.counter, "input", "running", message, started_at=now, updated_at=now)
        await self._phase("input", {"cycle_id": self.counter, "message": message})
        try:
            await self._phase("perception", {"message_length": len(message)})
            memories = self.engine.memory.search(message)
            await self._phase("attention", {"memory_candidates": len(memories)})
            ranked = self.engine.attention.score(message, [m.content for m in memories], urgency=self.engine.internal_state.state.arousal)
            uncertainty = max(.05, .8 - len(memories) * .1)
            state = self.engine.internal_state.observe(input_length=len(message), memory_count=len(memories), uncertainty=uncertainty)
            self.engine.meta = self.engine.metacognition.evaluate(state["uncertainty"], len(memories))
            self.engine.last_prediction = self.engine.prediction.predict(message, state["uncertainty"])
            settings = self.engine.settings_v2.snapshot()
            try:
                runtime_mode = RuntimeMode(settings.get("runtime_mode", "auto"))
            except ValueError:
                runtime_mode = RuntimeMode.AUTO
            runtime_request = RuntimeRequest(
                prompt=message,
                mode=runtime_mode,
                privacy=settings.get("runtime_privacy", "private"),
                task_type="conversation",
                require_local_memory=True,
                allow_cloud=bool(settings.get("allow_cloud_llm", False)),
                allow_remote=bool(settings.get("allow_remote_llm", False)),
                metadata={"parallel_strategy": settings.get("parallel_strategy", "judge"), "cycle_id": self.counter},
            )
            self.engine.workspace = {"input": message, "focus": message, "attention": [asdict(x) for x in ranked], "memories": [m.json() for m in memories], "model": self.engine.model.info(), "metacognition": self.engine.meta, "prediction": self.engine.last_prediction, "internal_state": state, "cycle_id": self.counter, "runtime_request": {"mode": runtime_request.mode.value, "privacy": runtime_request.privacy, "allow_cloud": runtime_request.allow_cloud, "allow_remote": runtime_request.allow_remote}}
            await self._phase("workspace", self.engine.workspace)
            await self._phase("memory", {"retrieved": len(memories), "federation": "local-first"})
            await self._phase("self_world", {"self": asdict(self.engine.self_model), "world_entities": len(self.engine.world.snapshot()["entities"])})
            await self._phase("internal_state", {"state": state, "status": self.engine.internal_state.status()})
            goals = self.engine.goals.active(); self.current.active_goal = goals[0] if goals else None
            await self._phase("goal_evaluation", {"active_goals": len(goals), "selected": self.current.active_goal})
            await self._phase("reasoning", {"confidence": self.engine.meta.get("confidence", 0)})
            if self.current.active_goal:
                plan = self.engine.planner.create(self.current.active_goal["title"]); self.current.plan_id = plan["id"]
                await self._phase("planning", {"plan_id": self.current.plan_id, "goal_id": self.current.active_goal["id"]})
            else: await self._phase("planning", {"plan_id": None, "reason": "no active goal"})
            await self._phase("safety", self.engine.safety.snapshot())
            await self._phase("execution", {"mode": "approval-gated local simulation", "plan_id": self.current.plan_id})
            runtime_result = await self.engine.runtime.generate(runtime_request, [m.content for m in memories])
            response = runtime_result.text
            self.engine.workspace["runtime_result"] = {"mode": runtime_result.mode, "provider": runtime_result.provider, "model": runtime_result.model, "confidence": runtime_result.confidence, "degraded": runtime_result.degraded, "latency_ms": runtime_result.latency_ms, "candidates": runtime_result.candidates}
            await self._phase("observation", {"response_length": len(response), "runtime": self.engine.workspace["runtime_result"]})
            saved = self.engine.memory.add("User: " + message + "\nSystem: " + response, kind="episodic", importance=.55, confidence=max(.1, 1-self.engine.internal_state.state.uncertainty), source="conversation")
            self.engine.last_reflection = self.engine.reflection.reflect(message, response, self.engine.memory.count(), self.engine.internal_state.state.uncertainty)
            await self._phase("reflection", asdict(self.engine.last_reflection))
            learned_items = []
            for lesson in self.engine.last_reflection.lessons:
                learned_items.append(self.engine.learning_v2.learn(lesson, "retrieve_then_verify", [f"cycle:{self.counter}"], self.engine.meta.get("confidence", .5), .6, "reflection"))
            learned = self.engine.internal_state.transition(energy_delta=-.01, valence_delta=.01)
            await self._phase("learning", {"memory_id": saved.id, "lesson_count": len(learned_items), "updates": learned_items, "state": learned})
            await self._phase("consolidation", {"deferred": True, "reason": "consolidation is managed by sleep cycle"})
            self.current.status = "completed"
            self.current.updated_at = datetime.now(timezone.utc).isoformat()
            episode = self.engine.autobiographical_v2.create(cycle_id=self.counter, title=(self.current.active_goal or {}).get("title", "Cognitive episode"), summary=f"Cycle {self.counter} completed through reflection and bounded learning.", input_text=message, response_summary=response, active_goal_id=(self.current.active_goal or {}).get("id"), plan_id=self.current.plan_id, importance=.55, confidence=self.engine.meta.get("confidence", .5), tags=["cognitive-cycle", "reflection", "learning"], metadata={"memory_id": saved.id, "completed_phases": self.current.completed_phases, "runtime_provider": runtime_result.provider, "runtime_mode": runtime_result.mode}, started_at=self.current.started_at, ended_at=self.current.updated_at)
            await self.engine.events.publish(Event("autobiographical.episode.created", {"cycle_id": self.counter, "episode_id": episode["id"]}))
            await self._phase("idle", {"cycle_id": self.counter, "status": "completed", "episode_id": episode["id"]})
            return {"response": response, "cycle": asdict(self.current), "episode": episode, "memories": [m.json() for m in memories], "state": self.engine.internal_state.snapshot(), "workspace": self.engine.workspace, "reflection": asdict(self.engine.last_reflection), "metacognition": self.engine.meta, "prediction": self.engine.last_prediction, "learning": learned_items}
        except Exception as exc:
            self.current.status = "failed"; self.current.error = str(exc); self.current.updated_at = datetime.now(timezone.utc).isoformat(); await self.engine.events.publish(Event("loop.failed", asdict(self.current))); raise

    def snapshot(self): return asdict(self.current)
