import os
import json
from dataclasses import asdict
from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .core.engine import CognitiveEngine
from .database import db

VERSION="1.8.0"; app=FastAPI(title="ConsciousCore",version=VERSION)
origins=[x.strip() for x in os.getenv("CONSCIOUSCORE_CORS","http://127.0.0.1:5173,http://localhost:5173").split(",") if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=["*"],allow_headers=["*"]); engine=CognitiveEngine()
class Chat(BaseModel): message:str=Field(min_length=1,max_length=20000)
class MemoryInput(BaseModel):
    content:str=Field(min_length=1,max_length=50000); kind:str="semantic"; importance:float=Field(default=.5,ge=0,le=1); confidence:float=Field(default=.7,ge=0,le=1); tags:list[str]=Field(default_factory=list); source:str="user"
class MemoryUpdate(BaseModel):
    kind:str|None=None; importance:float|None=Field(default=None,ge=0,le=1); confidence:float|None=Field(default=None,ge=0,le=1); tags:list[str]|None=None; source:str|None=None; consolidated:bool|None=None
class Goal(BaseModel): title:str=Field(min_length=1,max_length=500); priority:float=Field(default=.5,ge=0,le=1)
class PlanRequest(BaseModel): goal:str=Field(min_length=1,max_length=1000); constraints:list[str]=Field(default_factory=list)
class PlanStepUpdate(BaseModel): status:str
class EntityInput(BaseModel): id:str; label:str; kind:str="concept"
class RelationInput(BaseModel): source:str; relation:str; target:str; confidence:float=Field(default=.5,ge=0,le=1)
class ToolInput(BaseModel): name:str; description:str; risk:float=Field(default=.5,ge=0,le=1)
class ActionCheck(BaseModel): action:str; risk:float=Field(default=.5,ge=0,le=1)
class ModelRegister(BaseModel):
    model_id:str=Field(min_length=1,max_length=200); path:str=Field(min_length=1,max_length=2000); context_size:int=Field(default=4096,ge=256,le=131072); n_threads:int|None=Field(default=None,ge=1,le=256); n_gpu_layers:int=Field(default=0,ge=0,le=999)
class ModelActivate(BaseModel): model_id:str=Field(min_length=1,max_length=200)
def audit(event_type,payload): db.execute("INSERT INTO audit_logs(event_type,payload,created_at) VALUES(?,?,?)",(event_type,json.dumps(payload),datetime.now(timezone.utc).isoformat()))
@app.get("/health")
async def health(): return {"ok":True,"service":"ConsciousCore","version":VERSION}
@app.get("/api/state")
async def state(): return engine.snapshot()
@app.post("/api/chat")
async def chat(body:Chat): return await engine.process(body.message)
@app.get("/api/memory")
async def memories(q:str="",limit:int=20,kind:str|None=None,consolidated:bool|None=None):
    limit=max(1,min(limit,1000)); items=engine.memory.search(q,limit,kind,consolidated); return {"items":[m.json() for m in items],"stats":engine.memory.stats()}
@app.get("/api/memory/stats")
async def memory_stats(): return engine.memory.stats()
@app.get("/api/memory/{memory_id}")
async def get_memory(memory_id:int):
    m=engine.memory.get(memory_id)
    if not m: raise HTTPException(status_code=404,detail="memory_not_found")
    return m.json()
@app.post("/api/memory")
async def add_memory(body:MemoryInput):
    m=engine.memory.add(body.content,body.kind,body.importance,body.confidence,tags=body.tags,source=body.source); audit("memory.created",{"memory_id":m.id,"kind":m.kind}); return m.json()
@app.patch("/api/memory/{memory_id}")
async def update_memory(memory_id:int,body:MemoryUpdate):
    if body.kind is not None and body.kind not in __import__(".core.memory",fromlist=["MEMORY_KINDS"]).MEMORY_KINDS: raise HTTPException(status_code=400,detail="invalid_memory_kind")
    m=engine.memory.update(memory_id,body.importance,body.confidence,body.kind,body.tags,body.source,body.consolidated)
    if not m: raise HTTPException(status_code=404,detail="memory_not_found")
    audit("memory.updated",{"memory_id":memory_id}); return m.json()
@app.delete("/api/memory/{memory_id}")
async def delete_memory(memory_id:int):
    if not engine.memory.delete(memory_id): raise HTTPException(status_code=404,detail="memory_not_found")
    audit("memory.deleted",{"memory_id":memory_id}); return {"deleted":True,"id":memory_id}
@app.post("/api/memory/consolidate")
async def consolidate(): result=engine.sleep.run(); audit("memory.consolidated",result); return result
@app.get("/api/self")
async def self_model(): return engine.snapshot()["self"]
@app.get("/api/workspace")
async def workspace(): return engine.workspace
@app.get("/api/attention")
async def attention(): return {"focus":engine.workspace.get("focus"),"items":engine.workspace.get("attention",[]),"uncertainty":engine.state.uncertainty}
@app.get("/api/metacognition")
async def metacognition(): return engine.meta
@app.get("/api/prediction")
async def prediction(): return engine.last_prediction
@app.get("/api/world")
async def world(): return engine.world.snapshot()
@app.post("/api/world/entities")
async def add_entity(body:EntityInput): return engine.world.add_entity(body.id,body.label,body.kind)
@app.post("/api/world/relations")
async def add_relation(body:RelationInput): return engine.world.relate(body.source,body.relation,body.target,body.confidence)
@app.get("/api/goals")
async def goals(): return {"items":engine.goals.snapshot()}
@app.post("/api/goals")
async def add_goal(body:Goal): return asdict(engine.goals.add(body.title,body.priority))
@app.patch("/api/goals/{goal_id}")
async def update_goal(goal_id:int,progress:float|None=None,status:str|None=None):
    g=engine.goals.update(goal_id,progress,status); return asdict(g) if g else {"error":"goal_not_found"}
@app.get("/api/plans")
async def plans(limit:int=100): return {"items":engine.planner.list(limit)}
@app.post("/api/plans")
async def create_plan(body:PlanRequest):
    plan=engine.planner.create(body.goal,body.constraints); audit("plan.created",{"plan_id":plan["id"],"goal":body.goal}); return plan
@app.get("/api/plans/{plan_id}")
async def get_plan(plan_id:int):
    plan=engine.planner.get(plan_id)
    if not plan: raise HTTPException(status_code=404,detail="plan_not_found")
    return plan
@app.patch("/api/plans/{plan_id}/steps/{step_id}")
async def update_plan_step(plan_id:int,step_id:int,body:PlanStepUpdate):
    try: plan=engine.planner.update_step(plan_id,step_id,body.status)
    except ValueError as exc: raise HTTPException(status_code=400,detail=str(exc))
    if not plan: raise HTTPException(status_code=404,detail="plan_or_step_not_found")
    audit("plan.step.updated",{"plan_id":plan_id,"step_id":step_id,"status":body.status}); return plan
@app.delete("/api/plans/{plan_id}")
async def delete_plan(plan_id:int):
    deleted=engine.planner.delete(plan_id)
    if not deleted: raise HTTPException(status_code=404,detail="plan_not_found")
    audit("plan.deleted",{"plan_id":plan_id}); return {"deleted":True,"id":plan_id}
@app.get("/api/models")
async def models(): return engine.model_manager.list()
@app.post("/api/models/discover")
async def discover_models(): found=engine.model_manager.discover_gguf(); audit("models.discovered",{"models":found}); return {"discovered":found,**engine.model_manager.list()}
@app.post("/api/models/register")
async def register_model(body:ModelRegister):
    kwargs={"n_ctx":body.context_size,"n_gpu_layers":body.n_gpu_layers};
    if body.n_threads is not None: kwargs["n_threads"]=body.n_threads
    try: info=engine.model_manager.register_gguf(body.model_id,body.path,**kwargs)
    except (ValueError,OSError) as exc: raise HTTPException(status_code=400,detail=str(exc))
    audit("model.registered",{"model_id":body.model_id,"path":body.path}); return info
@app.post("/api/models/activate")
async def activate_model(body:ModelActivate):
    try: info=engine.activate_model(body.model_id)
    except KeyError: raise HTTPException(status_code=404,detail="model_not_found")
    audit("model.activated",{"model_id":body.model_id}); return info
@app.get("/api/models/active")
async def active_model(): return engine.model.info()
@app.get("/api/reflection")
async def get_reflection(): return {"reflection":asdict(engine.last_reflection) if engine.last_reflection else None,"history":engine.reflection.recent()}
@app.post("/api/reflection")
async def reflection():
    r=engine.reflection.reflect(engine.workspace.get("input",""),"",engine.memory.count(),engine.state.uncertainty); engine.last_reflection=r; return asdict(r)
@app.get("/api/safety")
async def safety(): return engine.safety.snapshot()
@app.post("/api/safety/check")
async def safety_check(body:ActionCheck): result=asdict(engine.safety.evaluate(body.action,body.risk)); audit("safety.check",{"request":body.model_dump(),"result":result}); return result
@app.get("/api/tools")
async def tools(): return {"items":engine.tools.snapshot()}
@app.post("/api/tools")
async def register_tool(body:ToolInput): return engine.tools.register(body.name,body.description,body.risk)
@app.get("/api/tools/{name}/authorize")
async def authorize_tool(name:str): result=engine.tools.authorize(name); audit("tool.authorization",{"tool":name,"result":result}); return result
@app.get("/api/sleep")
async def sleep_status(): return engine.sleep.snapshot()
@app.post("/api/sleep")
async def sleep(): return engine.sleep.run()
@app.get("/api/audit")
async def audit_logs(limit:int=100): return {"items":db.fetchall("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?",(max(1,min(limit,1000)),))}
@app.get("/api/settings")
async def settings(): return {"autonomy_level":1,"local_only":True,"cloud_models":False,"external_actions_require_approval":True}
@app.websocket("/ws/events")
async def events(ws:WebSocket):
    await ws.accept(); q=engine.events.subscribe()
    try:
        while True:
            e=await q.get(); await ws.send_json({"type":e.type,"payload":e.payload,"timestamp":e.timestamp})
    except Exception: engine.events.unsubscribe(q)
