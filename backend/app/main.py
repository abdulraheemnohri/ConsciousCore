import os
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .core.engine import CognitiveEngine

app = FastAPI(title="ConsciousCore", version="1.1.0")
origins = [x.strip() for x in os.getenv("CONSCIOUSCORE_CORS", "http://127.0.0.1:5173,http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["*"], allow_headers=["*"])
engine = CognitiveEngine()

class Chat(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
class MemoryInput(BaseModel):
    content: str = Field(min_length=1, max_length=50000)
    kind: str = "semantic"
    importance: float = Field(default=.5, ge=0, le=1)
    confidence: float = Field(default=.7, ge=0, le=1)
    tags: list[str] = []
    source: str = "user"
class Goal(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    priority: float = Field(default=.5, ge=0, le=1)

@app.get("/health")
async def health(): return {"ok": True, "service": "ConsciousCore", "version": "1.1.0"}
@app.get("/api/state")
async def state(): return engine.snapshot()
@app.post("/api/chat")
async def chat(body: Chat): return await engine.process(body.message)
@app.get("/api/memory")
async def memories(q: str = "", limit: int = 20):
    limit = max(1, min(limit, 1000))
    items = engine.memory.search(q, limit) if q else engine.memory.recent(limit)
    return {"items": [m.json() for m in items]}
@app.post("/api/memory")
async def add_memory(body: MemoryInput):
    return engine.memory.add(body.content, body.kind, body.importance, body.confidence, tags=body.tags, source=body.source).json()
@app.post("/api/memory/consolidate")
async def consolidate(): return {"consolidated": engine.memory.consolidate()}
@app.get("/api/self")
async def self_model(): return engine.snapshot()["self"]
@app.get("/api/workspace")
async def workspace(): return engine.workspace
@app.get("/api/attention")
async def attention(): return {"focus": engine.workspace.get("focus"), "uncertainty": engine.state.uncertainty}
@app.get("/api/goals")
async def goals(): return {"items": engine.goals}
@app.post("/api/goals")
async def add_goal(body: Goal):
    g = {"id": len(engine.goals)+1, "title": body.title, "priority": body.priority, "status": "active"}
    engine.goals.append(g)
    return g
@app.post("/api/reflection")
async def reflection():
    return {"lessons": ["Review recent memories and outcomes before future planning."], "note": "Structured self-review; not evidence of subjective experience."}
@app.get("/api/settings")
async def settings():
    return {"autonomy_level": 1, "local_only": True, "cloud_models": False, "external_actions_require_approval": True}
@app.websocket("/ws/events")
async def events(ws: WebSocket):
    await ws.accept(); q = engine.events.subscribe()
    try:
        while True:
            e = await q.get(); await ws.send_json({"type": e.type, "payload": e.payload, "timestamp": e.timestamp})
    except Exception:
        engine.events.unsubscribe(q)
