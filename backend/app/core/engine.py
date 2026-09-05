from dataclasses import dataclass,asdict
from .events import Event,EventBus
from .memory import MemoryStore

class FallbackModel:
    async def generate(self,prompt,context):
        return ('Relevant memory: '+context[0]+'\n\n' if context else '') + 'ConsciousCore received: '+prompt

@dataclass
class InternalState:
    arousal:float=.2; valence:float=0; uncertainty:float=.5; energy:float=1

@dataclass
class SelfModel:
    identity:str='ConsciousCore'; role:str='local cognitive system'

class CognitiveEngine:
    def __init__(self,model=None):
        self.model=model or FallbackModel(); self.memory=MemoryStore(); self.events=EventBus(); self.state=InternalState(); self.self_model=SelfModel(); self.workspace={}; self.goals=[]
    async def process(self,message):
        memories=self.memory.search(message)
        self.workspace={'input':message,'focus':message,'memories':[m.json() for m in memories]}
        self.state.uncertainty=max(.05,.8-len(memories)*.1)
        await self.events.publish(Event('workspace.updated',self.workspace))
        response=await self.model.generate(message,[m.content for m in memories])
        saved=self.memory.add('User: '+message+'\nSystem: '+response)
        await self.events.publish(Event('memory.created',saved.json()))
        return {'response':response,'memories':[m.json() for m in memories],'state':asdict(self.state),'workspace':self.workspace}
    def snapshot(self): return {'state':asdict(self.state),'self':asdict(self.self_model),'workspace':self.workspace,'memory_count':len(self.memory.items),'goals':self.goals}
