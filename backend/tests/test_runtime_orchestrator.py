import pytest
from app.runtime.orchestrator import RuntimeOrchestrator
from app.runtime.types import RuntimeMode, RuntimeRequest

class FakeModel:
    def info(self): return {"name":"local-test"}
    async def generate(self,prompt,context): return "local answer"

@pytest.mark.asyncio
async def test_parallel_race_uses_available_local_provider():
    o=RuntimeOrchestrator(FakeModel())
    r=await o.generate(RuntimeRequest(prompt="hello",mode=RuntimeMode.PARALLEL,candidates=["local"],privacy="private"))
    assert r.provider=="local" and r.mode=="parallel"

@pytest.mark.asyncio
async def test_parallel_consensus_returns_successful_result():
    o=RuntimeOrchestrator(FakeModel())
    r=await o.generate(RuntimeRequest(prompt="hello",mode=RuntimeMode.PARALLEL,candidates=["local"],metadata={"parallel_strategy":"consensus"}))
    assert r.text=="local answer"
