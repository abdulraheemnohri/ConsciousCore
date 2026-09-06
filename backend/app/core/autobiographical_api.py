from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

class EpisodeInput(BaseModel):
    cycle_id:int|None=None
    title:str=Field(default="Cognitive episode",max_length=240)
    summary:str=Field(default="",max_length=4000)
    input_text:str=Field(default="",max_length=12000)
    response_summary:str=Field(default="",max_length=4000)
    active_goal_id:int|None=None
    plan_id:int|None=None
    reflection_id:int|None=None
    learning_ids:list[int]=Field(default_factory=list)
    event_ids:list[int]=Field(default_factory=list)
    importance:float=Field(default=.5,ge=0,le=1)
    confidence:float=Field(default=.5,ge=0,le=1)
    tags:list[str]=Field(default_factory=list)
    metadata:dict=Field(default_factory=dict)
    started_at:str|None=None
    ended_at:str|None=None

class ArchiveInput(BaseModel):
    archived:bool=True

def create_router(engine):
    router=APIRouter(prefix="/api/autobiographical/v2",tags=["Autobiographical Memory V2"])
    @router.get("")
    async def snapshot(): return engine.autobiographical_v2.snapshot()
    @router.get("/episodes")
    async def episodes(limit:int=50,include_archived:bool=False): return {"items":engine.autobiographical_v2.list(limit,include_archived)}
    @router.get("/episodes/{episode_id}")
    async def episode(episode_id:int):
        item=engine.autobiographical_v2.get(episode_id)
        if not item: raise HTTPException(404,"episode_not_found")
        return item
    @router.post("/episodes")
    async def create_episode(body:EpisodeInput): return engine.autobiographical_v2.create(**body.model_dump())
    @router.get("/search")
    async def search(q:str="",limit:int=50,include_archived:bool=False): return {"items":engine.autobiographical_v2.search(q,limit,include_archived)}
    @router.get("/timeline")
    async def timeline(start:str|None=None,end:str|None=None,limit:int=100): return {"items":engine.autobiographical_v2.timeline(start,end,limit)}
    @router.get("/stats")
    async def stats(): return engine.autobiographical_v2.stats()
    @router.patch("/episodes/{episode_id}/archive")
    async def archive(episode_id:int,body:ArchiveInput):
        item=engine.autobiographical_v2.archive(episode_id,body.archived)
        if not item: raise HTTPException(404,"episode_not_found")
        return item
    return router
