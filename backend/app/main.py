import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .core.engine import CognitiveEngine

app = FastAPI(title="ConsciousCore", version="1.2.0")
origins = [x.strip() for x in os.getenv("CONSCIOUSCORE_CORS", "http://127.0.0.1:5173,http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])
engine = CognitiveEngine()

class Chat(BaseModel): message: str = Field(min_length=1, max_length=20000)
class MemoryInput(BaseModel):
    content: str = Field(min_length=1, max_length=50000); kind: str = "semantic"
    importance: float = Field(default=.5, ge=0, le=1); confidence: float = Field(default=.7, ge=0, le=1)
    tags: list[str] = []; source: str = "user"
class Goal(BaseModel): title: str = Field(min_length=1, max_length=500); priority: float = Field(default=.5, ge=0, le=1)
class PlanRequest(BaseModel): goal: str = Field(min_length=1, max_length=1000); constraints: list[str] = []

@app.get("/health")
async def health(): return {"ok": True, "service": "ConsciousCore", "version": "1.2.0"}
@app.get("/api/state")
async def state(): return engine.snapshot()
@app.post("/api/chat")
async def chat(body: Chat): return await engine.process(body.message)
@app.get("/api/memory")
async def memories(q: str = "", limit: int = 20):
    limit = max(1, min(limit, 1000)); items = engine.memory.search(q, limit) if q else engine.memory.recent(limit)
    return {"items": [m.json() for m in items]}
@app.post("/api/memory")
async def add_memory(body: MemoryInput): return engine.memory.add(body.content, body.kind, body.importance, body.confidence, tags=body.tags, source=body.source).json()
@app.post("/api/memory/consolidate")
async def consolidate(): return {"consolidated": engine.memory.consolidate()}
@app.get("/api/self")
async def self_model(): return engine.snapshot()["self"]
@app.get("/api/workspace")
async def workspace(): return engine.workspace
@app.get("/api/attention")
async def attention(): return {"focus": engine.workspace.get("focus"), "items": engine.workspace.get("attention", []), "uncertainty": engine.state.uncertainty}
@app.get("/api/goals")
async def goals(): return {"items": engine.goals.snapshot()}
@app.post("/api/goals")
async def add_goal(body: Goal): return asdict(engine.goals.add(body.title, body.priority))
@app.patch("/api/goals/{goal_id}")
async def update_goal(goal_id: int, progress: float | None = None, status: str | None = None):
    g = engine.goals.update(goal_id, progress, status)
    return asdict(g) if g else {"error": "goal_not_found"}
@app.post("/api/plans")
async def create_plan(body: PlanRequest): return engine.planner.create(body.goal, body.constraints)
@app.get("/api/reflection")
async def get_reflection(): return {"reflection": asdict(engine.last_reflection) if engine.last_reflection else None}
@app.post("/api/reflection")
async def reflection():
    r = engine.reflection.reflect(engine.workspace.get("input", ""), "", engine.memory.count(), engine.state.uncertainty)
    engine.last_reflection = r; return asdict(r)
@app.get("/api/settings")
async def settings(): return {"autonomy_level": 1, "local_only": True, "cloud_models": False, "external_actions_require_approval": True}
@app.websocket("/ws/events")
async def events(ws: WebSocket):
    await ws.accept(); q = engine.events.subscribe()
    try:
        while True:
            e = await q.get(); await ws.send_json({"type": e.type, "payload": e.payload, "timestamp": e.timestamp})
    except Exception:
        engine.events.unsubscribe(q)

from dataclasses import asdict
