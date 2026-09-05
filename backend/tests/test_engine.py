import pytest
from app.core.engine import CognitiveEngine

@pytest.mark.asyncio
async def test_pipeline_creates_memory():
    e=CognitiveEngine(); r=await e.process('hello conscious core')
    assert 'response' in r
    assert len(e.memory.items)==1

@pytest.mark.asyncio
async def test_memory_retrieval():
    e=CognitiveEngine(); e.memory.add('Python local AI memory system',importance=.9)
    r=await e.process('local AI memory')
    assert r['memories']
