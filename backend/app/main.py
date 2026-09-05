from fastapi import FastAPI,WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .core.engine import CognitiveEngine

app=FastAPI(title='ConsciousCore',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
engine=CognitiveEngine()
class Chat(BaseModel): message:str
class Goal(BaseModel): title:str; priority:float=.5

@app.get('/health')
async def health(): return {'ok':True,'service':'ConsciousCore'}
@app.get('/api/state')
async def state(): return engine.snapshot()
@app.post('/api/chat')
async def chat(body:Chat): return await engine.process(body.message)
@app.get('/api/memory')
async def memories(q:str='',limit:int=20): return {'items':[m.json() for m in (engine.memory.search(q,limit) if q else engine.memory.items[-limit:])]}
@app.post('/api/memory')
async def add_memory(body:dict): return engine.memory.add(body.get('content',''),body.get('kind','semantic'),body.get('importance',.5)).json()
@app.get('/api/self')
async def self_model(): return engine.snapshot()['self']
@app.get('/api/workspace')
async def workspace(): return engine.workspace
@app.get('/api/attention')
async def attention(): return {'focus':engine.workspace.get('focus'),'uncertainty':engine.state.uncertainty}
@app.get('/api/goals')
async def goals(): return {'items':engine.goals}
@app.post('/api/goals')
async def add_goal(body:Goal):
    g={'id':len(engine.goals)+1,'title':body.title,'priority':body.priority,'status':'active'}; engine.goals.append(g); return g
@app.post('/api/reflection')
async def reflection(): return {'lessons':['Review recent memories and outcomes before future planning.'],'note':'Structured self-review; not evidence of subjective experience.'}
@app.get('/api/settings')
async def settings(): return {'autonomy_level':1,'local_only':True,'cloud_models':False,'external_actions_require_approval':True}
@app.websocket('/ws/events')
async def events(ws:WebSocket):
    await ws.accept(); q=engine.events.subscribe()
    try:
        while True:
            e=await q.get(); await ws.send_json({'type':e.type,'payload':e.payload,'timestamp':e.timestamp})
    except Exception: engine.events.unsubscribe(q)
